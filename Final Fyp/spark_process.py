import sys
import os
os.environ['SPARK_HOME'] = "C:/spark-3.0.0-bin-hadoop2.7"
os.environ['HADOOP_HOME'] = "C:/winutils-master/hadoop-2.7.1"
sys.path.append("‪C:/spark-3.0.0-bin-hadoop2.7/python")
sys.path.append("‪C:/spark-3.0.0-bin-hadoop2.7/python/lib")

import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import unix_timestamp, from_unixtime
from pyspark.mllib.fpm import FPGrowth
from pyspark.sql import functions as F
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

spark = SparkSession.builder.appName("Fp-Growth").getOrCreate()

cred = credentials.Certificate('fp-growth-test-firebase-adminsdk-h1p13-dea07cc96a.json')
firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fp-growth-test.firebaseio.com/'})
ref = db.reference('Fp-Growth-User-1')


def getColumns(addr):

    try:
        df_org = spark.read.csv(addr, header="true", inferSchema=False)
        columns = df_org.columns
        return columns,df_org

    except:

        try:
            newAddr = addr.replace('\\','/')
            df_org = spark.read.csv(newAddr, header="true", inferSchema=False)
            columns = df_org.columns
            return columns,df_org

        except:
            return "error"



def FpGrowthWithFilterByBranch(dataframe,date,product,branch):

    df = dataframe.select([product, date, branch])

    df = df.withColumn("_Products_", F.concat(F.col(product), F.lit(","), F.col(branch)))
    df.na.drop()

    transactions_data = df.groupBy(date).agg(F.collect_list("_Products_").alias("transactions")).rdd.map(
        lambda x: x.transactions)
    unique_transactions = transactions_data.map(lambda x: list(set(x))).cache()

    model = FPGrowth.train(unique_transactions, 0.2, 10)
    result = model.freqItemsets().collect()

    return result

def FpGrowthWithFilterByCity(dataframe,date,product,city):

    df = dataframe.select([product, date, city])

    df = df.withColumn("_Products_", F.concat(F.col(product), F.lit(","), F.col(city)))
    df.na.drop()

    transactions_data = df.groupBy(date).agg(F.collect_list("_Products_").alias("transactions")).rdd.map(
        lambda x: x.transactions)
    unique_transactions = transactions_data.map(lambda x: list(set(x))).cache()

    model = FPGrowth.train(unique_transactions, 0.2, 10)
    result = model.freqItemsets().collect()

    return result

def FpGrowthWithFilterByOverall(dataframe,date,product):

    df = dataframe.select([product, date])
    df.na.drop()

    transactions_data = df.groupBy(date).agg(F.collect_list(product).alias("transactions")).rdd.map(
        lambda x: x.transactions)
    unique_transactions = transactions_data.map(lambda x: list(set(x))).cache()

    model = FPGrowth.train(unique_transactions, 0.2, 10)
    result = model.freqItemsets().collect()

    return result

def WriteResultsForOverall(result):


    print("\n Data for  overall is saving to firebase.......")

    itemChainNumber = 1
    itemNumber = 1

    for fi in result:

        user_ref_1 = ref.child('ItemChain_With_Filter_By_Overall').child('ItemChain-' + str(itemChainNumber))
        itemChain_Info = list(fi)
        itemNamesList = itemChain_Info[0]
        chainFrequency = itemChain_Info[1]

        for x in itemNamesList:
            List1 = x.split(',')
            user_ref_1.update({
                'Item' + str(itemNumber): {
                    'ItemName': List1[0],
                }})
            itemNumber = itemNumber + 1

        user_ref_1.update({
            'Chain-Frequency': {
                'frequency': chainFrequency
            }})

        itemNumber = 1
        itemChainNumber = itemChainNumber + 1

def WriteResultsForBranch(result):

    print("\n Data for branch filter is saving to firebase.......")

    itemChainNumber = 1
    itemNumber = 1

    for fi in result:


        user_ref_1 = ref.child('ItemChain_With_Filter_By_Branch').child('ItemChain-' + str(itemChainNumber))
        itemChain_Info = list(fi)
        itemNamesList = itemChain_Info[0]
        chainFrequency = itemChain_Info[1]

        for x in itemNamesList:
            List1 = x.split(',')
            user_ref_1.update({
                'Item' + str(itemNumber): {
                    'ItemName': List1[0],
                    'Branch': List1[1],
                }})
            itemNumber = itemNumber + 1

        user_ref_1.update({
            'Chain-Frequency': {
                'frequency': chainFrequency
            }})

        itemNumber = 1
        itemChainNumber = itemChainNumber + 1


def WriteResultsForCity(result):

    print("\n Data for city filter is saving to firebase.......")

    itemChainNumber = 1
    itemNumber = 1

    for fi in result:

        user_ref_1 = ref.child('ItemChain_With_Filter_By_City').child('ItemChain-'+str(itemChainNumber))
        itemChain_Info = list(fi)
        itemNamesList = itemChain_Info[0]
        chainFrequency = itemChain_Info[1]

        for x in itemNamesList:
            List1 = x.split(',')
            user_ref_1.update({
                'Item'+str(itemNumber) : {
                    'ItemName': List1[0],
                    'City': List1[1],
                }})
            itemNumber = itemNumber + 1

        user_ref_1.update({
            'Chain-Frequency': {
                'frequency' : chainFrequency
            }})

        itemNumber = 1
        itemChainNumber = itemChainNumber + 1

