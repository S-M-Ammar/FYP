import sys
import os
os.environ['SPARK_HOME'] = "C:/spark-3.0.0-bin-hadoop2.7"
os.environ['HADOOP_HOME'] = "C:/winutils-master/hadoop-2.7.1"
sys.path.append("‪C:/spark-3.0.0-bin-hadoop2.7/python")
sys.path.append("‪C:/spark-3.0.0-bin-hadoop2.7/python/lib")

from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer

from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db




spark = SparkSession.builder.appName("Customer").getOrCreate()

cols_to_compare = []
TargetCol_to_compare = []
finalCols = {}
def readData_with_schema(addr):
    try:
        df_org = spark.read.csv(addr, header="true", inferSchema='true')
        return df_org

    except:

        try:
            newAddr = addr.replace('\\','/')
            df_org = spark.read.csv(newAddr, header="true", inferSchema='true')
            return df_org

        except:
            return "error"

def get_Indexer_dict(df):
    cat_cols = get_cat_cols(df)
    copy_df = df
    indexer_dict = {}
    for x in cat_cols:
        indexer = StringIndexer(inputCol=x, outputCol=x+"indexed")
        indexed = indexer.fit(copy_df).transform(copy_df)
        indexer_dict[x] = indexed


    return indexer_dict

def get_cat_cols(df):

    cat_cols = []
    for s in df.schema:
        data_type = str(s.dataType)
        if data_type == "StringType":
            cat_cols.append(s.name)

    return cat_cols

def removeCols(dataframe,cols_to_remove):
    cols_drop = cols_to_remove
    df_copy = dataframe
    df_copy = df_copy.drop(*cols_drop)
    return df_copy

def convertCatColumns(df):
    cat_cols = get_cat_cols(df)
    indexer_dict = {}
    for x in cat_cols:
        indexer = StringIndexer(inputCol=x, outputCol=x + "indexed")
        indexed = indexer.fit(df).transform(df)
        indexer_dict[x] = indexed
        df = indexed

    return df

def get_inputCols_for_Model(target_col, df):
    col_list = df.columns
    if (target_col in col_list):
        target_index = col_list.index(target_col)
        col_list.pop(target_index)
        return col_list, target_col

    else:
        target_col = str(target_col + "indexed")
        target_index = col_list.index(target_col)
        col_list.pop(target_index)
        return col_list, target_col

def getting_features_vectorAssembler(df,targetCol):

    input_cols , targetCol = get_inputCols_for_Model(targetCol,df)
    assembler = VectorAssembler(inputCols=input_cols,outputCol='features')
    final_df = assembler.transform(df)
    final_df = final_df.select(['features',targetCol])
    return final_df,targetCol

def trainModel(cols_to_remove,targetCol,pathList):

    TargetCol_to_compare.clear()
    TargetCol_to_compare.append(targetCol)

    #getting data with original schema
    pathList[0] = pathList[0].replace("/", "\\")
    df = readData_with_schema(pathList[0])

    if(isinstance(df, str)):
        return "Invalid Address"

    #remove un-important features
    df = removeCols(df,cols_to_remove)
    cols_to_compare.clear()
    cols_to_compare.append(df.columns)

    # removing NaN values
    df = df.dropna(how="any", subset=df.columns)

    indexer_dict = get_Indexer_dict(df)
    df = convertCatColumns(df)

    cat_cols = get_cat_cols(df)
    df = df.drop(*cat_cols)

    final_df, targetCol = getting_features_vectorAssembler(df, "Exited")
    print(final_df.show())
    train_data, test_data = final_df.randomSplit([0.80, 0.20])
    # random forest Model

    rfc = RandomForestClassifier(labelCol=targetCol, featuresCol='features', numTrees=100)
    rfc_model = rfc.fit(train_data)
    rfc_preds = rfc_model.transform(test_data)
    my_binary_eval = BinaryClassificationEvaluator(labelCol=targetCol)
    accuracy = my_binary_eval.evaluate(rfc_preds)
    Feature_Importance = rfc_model.featureImportances
    print(cols_to_compare)
    return accuracy,Feature_Importance,rfc_model

def make_churn_predictions(rfc_model,dataframe_addr,targetCol_org,cols_to_remove):

    #This function will send a tuple (error flag,error statement,None) if error occurs
    #otherwise it will send (Flase,"",predictionList)

    general_error_flag = False

    df_pred = readData_with_schema(dataframe_addr)

    Error_0 = "Invalid Data. Can't find data file."
    Error_0_flag = False

    if(isinstance(df_pred,str)):
        Error_0_flag = True
        return (Error_0_flag,Error_0,None)

    df_copy_pred = df_pred

    #checking if data-frame holds all required input cols

    flag = True
    cols_check = cols_to_compare[0]
    print(cols_check)
    try:
        cols_check.remove(targetCol_org)
        finalCols[0] = cols_check
    except:
        pass


    # now check if all required input cols are present in new dataset
    Error_1 = "Input Column Missing"
    Error_1_flag = False
    try:
        for x in cols_check:
            if x not in df_copy_pred.columns:
                Error_1_flag = True
                return (Error_1_flag,Error_1,None)
    except Exception as exception:
        print(exception)


    #removing targetCol from new input columns
    df_copy_pred = df_copy_pred.select(*cols_check)

    Error_2 = "Something wrong with the input columns"
    Error_2_flag = False

    try:
        #Converting columns into proper datatype
        df_copy_pred = convertCatColumns(df_copy_pred)
        cat_cols = get_cat_cols(df_copy_pred)
        df_copy_pred = df_copy_pred.drop(*cat_cols)
        assembler = VectorAssembler(inputCols=df_copy_pred.columns, outputCol='features')
        df_copy_pred_final = assembler.transform(df_copy_pred)
    except Exception as exception:
        Error_2_flag = True
        print(exception)
        return (Error_2_flag,Error_2,None)

    if(Error_0_flag==False and Error_1_flag==False and Error_2_flag==False):
        rfc_preds = rfc_model.transform(df_copy_pred_final)
        predictions_list =[]
        predictions = rfc_preds.select("prediction").collect()
        for x in predictions:
            predictions_list.append(x[0])

        return (False,"",predictions_list)


def upload_predictions(predictionList,featureImportance):

    try:
        ref = db.reference('Churn-Prediction-User-1')
    except Exception as exception:
        print(exception)


    user_ref_1 = ref.child("Predictions")
    i = 1
    for x in predictionList:
        user_ref_1.update({
            'Prediction_' + str(i): {
                'Customer_number':i,
                'Value': x,
            }})
        i += 1

    user_ref_1 = ref.child("Feature_Importance")
    j=0
    for x in featureImportance[0]:
        user_ref_1.update({
            'Feature_Importance' + str(j): {
                'Feature_Name': finalCols[0][j],
                'Value': round(x*100,2),
            }})
        j+=1

    # print("-----")
    # print(type(featureImportance[0]))
    # attribute_index = 0
    # for x in featureImportance[0]:
    #     try:
    #         print("Attribute : ",finalCols[0][attribute_index],"   Importance : ",round(x*100,2))
    #         attribute_index+=1
    #     except Exception as exception:
    #         print(exception)



