from PyQt5.QtWidgets import QWidget,QMainWindow,QFileDialog,QPushButton,QMessageBox,QListWidget,QLineEdit,QApplication,QDialog,QHBoxLayout,QVBoxLayout,QGroupBox,QGridLayout,QLabel,QRadioButton
import sys
from PyQt5 import QtGui
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QRect
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread
import spark_process
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime
import spark_process_customer



#global Variables
pathList_2 = []
pathList=[]
col_list =[]
dataframe = [] # 0 index data-frame
filter_dictionary = {'date':None,'branch':None,'product':None,'city':None}
branch_result_list = []
city_result_list = []
overall_result_list = []
cols_to_be_removed = []
TargetClass_for_customer = []
model_accuracy = []
feature_importance = []
classifier_model = []
predictions = []
out_dict_customer = {}


class upload_customer_predictions(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        spark_process_customer.upload_predictions(out_dict_customer[0][2],feature_importance)

class make_predictions(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        error_tuple_customer = spark_process_customer.make_churn_predictions(classifier_model[0],pathList_2[0],TargetClass_for_customer[0],cols_to_be_removed)
        out_dict_customer[0] = error_tuple_customer

class prepare_Model_for_chunk_prediction(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        acc , feature_imp , model = spark_process_customer.trainModel(cols_to_be_removed,TargetClass_for_customer[0],pathList)
        model_accuracy.clear()
        feature_importance.clear()
        classifier_model.clear()

        model_accuracy.append(acc)
        feature_importance.append(feature_imp)
        classifier_model.append(model)

        print(model_accuracy)
        print(feature_importance)

class WriteResultForBranch(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        spark_process.WriteResultsForBranch(branch_result_list[0])

class WriteResultForCity(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        spark_process.WriteResultsForCity(city_result_list[0])

class WriteResultForOverall(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        spark_process.WriteResultsForOverall(overall_result_list[0])

class fpGrowth_Thread_for_Branch(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
             branch_result = spark_process.FpGrowthWithFilterByBranch(dataframe=dataframe[0],date=filter_dictionary['date'],product=filter_dictionary['product'],branch=filter_dictionary['branch'])
             branch_result_list.append(branch_result)

class fpGrowth_Thread_for_City(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        city_result = spark_process.FpGrowthWithFilterByCity(dataframe=dataframe[0], date=filter_dictionary['date'], product=filter_dictionary['product'],city=filter_dictionary['city'])
        city_result_list.append(city_result)

class fpGrowth_Thread_for_Overall(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        overall_result = spark_process.FpGrowthWithFilterByOverall(dataframe=dataframe[0], date=filter_dictionary['date'],product=filter_dictionary['product'])
        overall_result_list.append(overall_result)

class getColumns_Thread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):

        pathList[0]= pathList[0].replace("/","\\")
        columns,df_org = spark_process.getColumns(pathList[0])
        col_list.append(columns)
        dataframe.append(df_org)

class Window(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Login Window"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250


        self.Init_Window()

    def Init_Window(self):
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)

        self.showMaximized()


    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox.setStyleSheet('background-color:rgb(255,255,255)')
        gridLayout = QGridLayout()


        self.AdminImage = QLabel()
        pixmap = QPixmap("admin.png")
        self.AdminImage.setPixmap(pixmap)
        self.setMinimumHeight(100)
        self.setMinimumWidth(200)


        self.dummylabel_1 = QLabel("")
        self.setMinimumHeight(40)
        self.setMinimumWidth(40)


        self.label = QLabel("\tEnter Your ID ")
        self.label.setFont(QtGui.QFont("arial", 20))
        self.label.setStyleSheet('color:rgb(8,0,0)')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label,0,1)

        self.Name_LineEdit = QLineEdit()
        self.Name_LineEdit.setFont(QtGui.QFont("Arial",20))
        self.Name_LineEdit.setMaximumWidth(500)
        self.Name_LineEdit.setMaximumHeight(40)
        gridLayout.addWidget(self.Name_LineEdit,0,2)

        self.groupBox_2 = QGroupBox()
        self.groupBox_2.setStyleSheet('background-color:rgb(255,255,255)')
        gridLayout_2 = QGridLayout()
        gridLayout.addWidget(self.dummylabel_1,0,3)
        gridLayout.addWidget(self.groupBox_2,0,4)


        gridLayout_2.addWidget(self.AdminImage,1,0)

        gridLayout.addWidget(self.dummylabel_1, 1, 0)
        self.label_1 = QLabel("\tEnter Your Pass ")
        self.label_1.setFont(QtGui.QFont("arial", 20))
        self.label_1.setStyleSheet('color:rgb(8,0,0)')
        self.label_1.setMinimumWidth(5)
        self.label_1.setMinimumHeight(40)
        gridLayout.addWidget(self.label_1, 2, 1)


        self.Pass_LineEdit = QLineEdit()
        self.Pass_LineEdit.setEchoMode(QLineEdit.Password)
        self.Pass_LineEdit.setFont(QtGui.QFont("Arial", 20))
        self.Pass_LineEdit.setMaximumWidth(500)
        self.Pass_LineEdit.setMaximumHeight(40)
        gridLayout.addWidget(self.Pass_LineEdit, 2, 2)

        gridLayout.addWidget(self.dummylabel_1, 3, 1)
        gridLayout.addWidget(self.dummylabel_1, 4, 0)



        button = QPushButton("LOGIN")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn)
        gridLayout.addWidget(button,5,4)

        button_close = QPushButton("CLOSE")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application)
        gridLayout.addWidget(button_close, 5, 1)


        self.groupBox.setLayout(gridLayout)
        self.groupBox_2.setLayout(gridLayout_2)



    def Click_Next_btn(self):

         if(self.Name_LineEdit.text()=="admin" and self.Pass_LineEdit.text()=="1234"):

            self.window = Window_File_Selection()
            self.destroy()



    def Close_Application(self):
        #self.label.setText("I AM CLICKED")
        sys.exit()

class Window_File_Selection(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "File selection"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.file_path = None


        self.Init_Window_1()

    def Init_Window_1(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout_1()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)
        self.showMaximized()

    def createLayout_1(self):

        self.groupBox = QGroupBox("")
        self.groupBox2 = QGroupBox("")
        self.groupBox2.setStyleSheet('background-color:white')
        self.groupBox.setStyleSheet('background-color:white')
        gridLayout = QGridLayout()
        gridLayout_2 = QGridLayout()

        self.dummylabel_1 = QLabel("")
        self.setMinimumHeight(40)
        self.setMinimumWidth(40)

        self.File_search_logo = QLabel("")
        pixmap = QPixmap("File_search.png")
        self.File_search_logo.setPixmap(pixmap)
        self.File_search_logo.setFixedHeight(450)
        self.File_search_logo.setFixedWidth(450)



        self.label = QLabel("Kindly browse your data file.\nYour file must be in csv format.")
        self.label.setFont(QtGui.QFont("Arial", 20))
        self.label.setStyleSheet('color:black')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label, 0, 0)
        gridLayout.addWidget(self.groupBox2,2,5)
        gridLayout.addWidget(self.dummylabel_1, 2, 0)
        gridLayout.addWidget(self.dummylabel_1, 2, 1)
        gridLayout.addWidget(self.dummylabel_1, 2, 3)
        gridLayout.addWidget(self.dummylabel_1, 2, 4)
        gridLayout_2.addWidget(self.File_search_logo,0,0)


        gridLayout.addWidget(self.dummylabel_1, 3, 0)
        gridLayout.addWidget(self.dummylabel_1, 4, 0)

        button = QPushButton("Browse File")
        button.setIcon(QtGui.QIcon("search_icon.png"))
        button.setIconSize(QtCore.QSize(70, 70))
        button.setFont(QtGui.QFont("Arial", 15))
        button.setStyleSheet('color:white; background-color:rgb(128, 128, 128)')
        button.setFixedWidth(270)
        button.setFixedHeight(120)
        button.clicked.connect(self.file_open_for_processing)
        gridLayout.addWidget(button, 2,1)

        button = QPushButton("Next")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn_1)
        gridLayout.addWidget(button, 5, 6)

        button_close = QPushButton("Back")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application_1)
        gridLayout.addWidget(button_close, 5, 0)

        self.groupBox.setLayout(gridLayout)
        self.groupBox2.setLayout(gridLayout_2)


    def file_open_for_processing(self):
        self.file_path = None
        pathList.clear()
        self.file_path =QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')


    def Close_Application_1(self):
        sys.exit()

    def Click_Next_btn_1(self):

        if(self.file_path!=None and self.file_path[0]!=""):
            pathList.append(self.file_path[0])
            self.workerThread_1 = getColumns_Thread()
            self.workerThread_1.start()
            self.window = Window_Data_Type(self.workerThread_1)
            self.destroy()

class Window_Data_Type(QDialog):

    def __init__(self,worker_thread):
        super().__init__()
        self.title = "Data Type Selection"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.thread_instance = worker_thread
        self.Init_Window()
        self.sales_flag = False
        self.customer_flag = False
        self.columnsLoad = False

    def Init_Window(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)
        self.thread_instance.finished.connect(self.update_label)
        self.showMaximized()

    def createLayout(self):

        self.groupBox = QGroupBox("")
        self.groupBox.setStyleSheet('background-color:white')
        gridLayout = QGridLayout()

        self.dummylabel_1 = QLabel("")
        self.setMinimumHeight(40)
        self.setMinimumWidth(40)

        self.label = QLabel("Select Your Data Type.")
        self.label.setFont(QtGui.QFont("Arial", 20))
        self.label.setStyleSheet('color:black')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label, 0, 0)

        self.radiobtn = QRadioButton("Sales Date")
        self.radiobtn.toggled.connect(self.Radio_Sales_btn)
        self.radiobtn.setIcon(QtGui.QIcon("sales_icon.jpg"))
        self.radiobtn.setIconSize(QtCore.QSize(300, 400))
        self.radiobtn.setFont(QtGui.QFont("Arial", 18))
        gridLayout.addWidget(self.radiobtn, 2, 0)

        gridLayout.addWidget(self.dummylabel_1,2,1)

        self.radiobtn1 = QRadioButton("Customer Data")
        self.radiobtn1.toggled.connect(self.Radio_Customer_btn)
        self.radiobtn1.setIcon(QtGui.QIcon("customer_icon.jpg"))
        self.radiobtn1.setIconSize(QtCore.QSize(300, 400))
        self.radiobtn1.setFont(QtGui.QFont("Arial", 18))
        gridLayout.addWidget(self.radiobtn1, 2, 2)

        button = QPushButton("Next")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn_1)
        gridLayout.addWidget(button, 3, 3)

        button_close = QPushButton("Back")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application_1)
        gridLayout.addWidget(button_close, 3, 0)

        self.label_loading = QLabel("Please wait.\nFile is in process")
        self.label_loading.setFont(QtGui.QFont("Arial", 14))
        self.label_loading.setStyleSheet('color:red')
        self.label_loading.setMinimumWidth(26)
        self.label_loading.setMinimumHeight(40)
        gridLayout.addWidget(self.label_loading, 1, 1)



        self.groupBox.setLayout(gridLayout)


    def update_label(self):
        self.columnsLoad = True
        self.label_loading.setText("Kindly Proceed")

    def Radio_Sales_btn(self):
        radio_btn = self.sender()
        if (radio_btn.isChecked()):
            print("Sales is selected")
            self.customer_flag = False
            self.sales_flag = True

    def Radio_Customer_btn(self):
        radio_btn = self.sender()
        if (radio_btn.isChecked()):
            print("Customer is selected")
            self.customer_flag = True
            self.sales_flag = False

    def Close_Application_1(self):
        sys.exit()

    def Click_Next_btn_1(self):
        if(self.columnsLoad==True):

            if(self.sales_flag==True):
                self.window = select_Columns_For_Sales()
                print(dataframe[0])
                self.destroy()

            if(self.customer_flag==True):
                self.window = select_columns_for_customer()
                print(dataframe[0])
                self.destroy()

class select_columns_for_customer(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Columns Display"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.Init_Window()

    def Init_Window(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)
        self.showMaximized()


    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox.setStyleSheet('background-color:white')
        gridLayout = QGridLayout()

        self.label = QLabel("Following are the columns of your dataset. Kindly select the columns which are not important in terms of\ndata analytics. Select the columns such as id, phone number, name, address, email. These columns will be\nremoved for better prediction")
        self.label.setFont(QtGui.QFont("Arial", 18))
        self.label.setStyleSheet('color:red')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label, 0, 0)

        self.col_remove_list = QListWidget()
        self.col_remove_list.setSelectionMode(QListWidget.MultiSelection)
        i=0
        for x in col_list[0]:
            self.col_remove_list.insertItem(i,x)
            i+=1

        gridLayout.addWidget(self.col_remove_list, 1, 0)

        button = QPushButton("Next")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn_1)
        gridLayout.addWidget(button, 4, 3)

        button_close = QPushButton("Back")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application_1)
        gridLayout.addWidget(button_close, 4, 0)

        self.groupBox.setLayout(gridLayout)


    def Close_Application_1(self):
        sys.exit()

    def Click_Next_btn_1(self):
        cols_to_be_removed.clear()
        for x in self.col_remove_list.selectedItems():
            cols_to_be_removed.append(x.text())

        self.window = select_target_class_for_customer()
        self.destroy()

class select_target_class_for_customer(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "Target Class Selection"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.Init_Window()

    def Init_Window(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)
        self.showMaximized()

    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox.setStyleSheet('background-color:white')
        gridLayout = QGridLayout()

        self.label = QLabel("Following are the columns of your dataset. Kindly select the target class which has to predicted")
        self.label.setFont(QtGui.QFont("Arial", 18))
        self.label.setStyleSheet('color:red')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label, 0, 0)

        self.col_target = QListWidget()
        i = 0
        for x in col_list[0]:
            self.col_target.insertItem(i, x)
            i += 1

        gridLayout.addWidget(self.col_target, 1, 0)

        button = QPushButton("Next")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn_1)
        gridLayout.addWidget(button, 4, 3)

        button_close = QPushButton("Back")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application_1)
        gridLayout.addWidget(button_close, 4, 0)

        self.groupBox.setLayout(gridLayout)

    def Close_Application_1(self):
        sys.exit()

    def Click_Next_btn_1(self):

        TargetClass_for_customer.clear()
        TargetClass_for_customer.append(self.col_target.selectedItems()[0].text())
        print(TargetClass_for_customer)

        self.window = Model_loading_Screen_customer()
        self.destroy()

class select_Columns_For_Sales(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Columns Display"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.Date = ""
        self.product = ""
        self.Init_Window()

    def Init_Window(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)
        self.showMaximized()

    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox.setStyleSheet('background-color:white')
        gridLayout = QGridLayout()

        self.label = QLabel("Select Column for Date")
        self.label.setFont(QtGui.QFont("Arial", 18))
        self.label.setStyleSheet('color:red')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label, 0, 0)

        self.label_2 = QLabel("Select Column for Products")
        self.label_2.setFont(QtGui.QFont("Arial", 18))
        self.label_2.setStyleSheet('color:red')
        self.label_2.setMinimumWidth(5)
        self.label_2.setMinimumHeight(40)
        gridLayout.addWidget(self.label_2, 2, 0)


        i=0
        self.list = QListWidget()
        self.list.clicked.connect(self.listview_Date_clicked)
        self.list_1 = QListWidget()
        self.list_1.clicked.connect(self.listview_product_clicked)
        for x in col_list[0]:
            self.list.insertItem(i,x)
            self.list_1.insertItem(i,x)
            i+=1

        gridLayout.addWidget(self.list,1,0)
        gridLayout.addWidget(self.list_1,3,0)

        button = QPushButton("Next")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn_1)
        gridLayout.addWidget(button, 4, 3)

        button_close = QPushButton("Back")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application_1)
        gridLayout.addWidget(button_close, 4, 0)


        self.groupBox.setLayout(gridLayout)

    def Close_Application_1(self):
        sys.exit()

    def Click_Next_btn_1(self):

        if(self.Date==""):
            print("You must select one date column")

        elif(self.product==""):
            print("You must select one product column")

        elif(self.Date==self.product):
            print("Date and product column cannot be same")

        else:
            print(self.Date)
            print(self.product)
            filter_dictionary['date'] = self.Date
            filter_dictionary['product'] = self.product
            self.window = selectBranch_City_Filter()
            self.destroy()

    def listview_Date_clicked(self):
        item = self.list.currentItem()
        self.Date = str(item.text())

    def listview_product_clicked(self):
        item = self.list_1.currentItem()
        self.product = str(item.text())

class selectBranch_City_Filter(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Branch / City Filter"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.Branch = None
        self.City = None
        self.Init_Window()

    def Init_Window(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)
        self.showMaximized()

    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox.setStyleSheet('background-color:white')
        gridLayout = QGridLayout()

        self.label = QLabel("Select Column for Branch (Optional) ")
        self.label.setFont(QtGui.QFont("Arial", 18))
        self.label.setStyleSheet('color:red')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label, 0, 0)

        self.label_2 = QLabel("Select Column for City (Optional) ")
        self.label_2.setFont(QtGui.QFont("Arial", 18))
        self.label_2.setStyleSheet('color:red')
        self.label_2.setMinimumWidth(5)
        self.label_2.setMinimumHeight(40)
        gridLayout.addWidget(self.label_2, 2, 0)


        i=0
        self.list = QListWidget()
        self.list.clicked.connect(self.listview_Branch_clicked)
        self.list_1 = QListWidget()
        self.list_1.clicked.connect(self.listview_City_clicked)
        for x in col_list[0]:
            self.list.insertItem(i,x)
            self.list_1.insertItem(i,x)
            i+=1

        gridLayout.addWidget(self.list,1,0)
        gridLayout.addWidget(self.list_1,3,0)

        button = QPushButton("Next")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn_1)
        gridLayout.addWidget(button, 4, 3)

        button_close = QPushButton("Back")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application_1)
        gridLayout.addWidget(button_close, 4, 0)


        self.groupBox.setLayout(gridLayout)

    def Close_Application_1(self):
        sys.exit()

    def Click_Next_btn_1(self):


        if(self.City==self.Branch and self.City!=None and self.Branch!=None):
            print("Branch and City column cannot be same")

        elif (self.Branch == filter_dictionary['date']):
            print("Branch and date column cannot be same")

        elif (self.City == filter_dictionary['date']):
            print("City and date column cannot be same")

        elif (self.Branch == filter_dictionary['product']):
            print("Branch and product column cannot be same")

        elif (self.City == filter_dictionary['product']):
            print("City and  column cannot be same")

        else:
            print(self.Branch)
            print(self.City)
            filter_dictionary['branch'] = self.Branch
            filter_dictionary['city'] = self.City
            self.window = Final_Window_Sales()
            self.destroy()

    def listview_Branch_clicked(self):
        item = self.list.currentItem()
        self.Branch = str(item.text())

    def listview_City_clicked(self):
        item = self.list_1.currentItem()
        self.City = str(item.text())

class Final_Window_Sales(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Final Window"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.model_overall = True
        self.model_branch = False
        self.model_city = False
        self.city_firebase = False
        self.overall_firebase = False
        self.branch_firebase = False


        self.Init_Window()

    def Init_Window(self):

        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.vbox.addWidget(self.groupBox2)
        self.setLayout(self.vbox)

        self.showMaximized()


    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox2 = QGroupBox("")

        self.groupBox.setStyleSheet('background-color:rgb(255,255,255)')
        self.groupBox2.setStyleSheet('background-color:rgb(255,255,255)')

        self.dummy_label = QLabel("")
        self.dummy_label.setMinimumHeight(20)
        self.dummy_label.setMinimumWidth(20)

        gridLayout = QGridLayout()
        self.gridLayout2 = QGridLayout()

        # currentDT = datetime.datetime.now()
        # currentDT = str(currentDT)

        self.label_log_1 = QLabel("Status: Model Training")
        self.label_log_1.setFont(QtGui.QFont("Arial", 10))
        self.label_log_1.setStyleSheet('color:green')
        self.label_log_1.setFixedHeight(20)
        self.label_log_1.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_1,0,0)

        self.label_log_2 = QLabel("FP GROWTH MODEL Initializing....")
        self.label_log_2.setFont(QtGui.QFont("Arial", 10))
        self.label_log_2.setStyleSheet('color:green')
        self.label_log_2.setFixedHeight(20)
        self.label_log_2.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_2, 1, 0)

        self.label_log_3 = QLabel("Processing...")
        self.label_log_3.setFont(QtGui.QFont("Arial", 10))
        self.label_log_3.setStyleSheet('color:green')
        self.label_log_3.setFixedHeight(20)
        self.label_log_3.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_3, 2, 0)

        self.label_fp_overall = QLabel("")
        self.label_fp_overall.setFont(QtGui.QFont("Arial", 10))
        self.label_fp_overall.setStyleSheet('color:green')
        self.label_fp_overall.setFixedHeight(20)
        self.label_fp_overall.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_fp_overall, 3, 0)

        self.label_fp_branch = QLabel("")
        self.label_fp_branch.setFont(QtGui.QFont("Arial", 10))
        self.label_fp_branch.setStyleSheet('color:green')
        self.label_fp_branch.setFixedHeight(20)
        self.label_fp_branch.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_fp_branch, 4, 0)

        self.label_fp_city = QLabel("")
        self.label_fp_city.setFont(QtGui.QFont("Arial", 10))
        self.label_fp_city.setStyleSheet('color:green')
        self.label_fp_city.setFixedHeight(20)
        self.label_fp_city.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_fp_city, 5, 0)

        self.label_fp_overall_firebase = QLabel("")
        self.label_fp_overall_firebase.setFont(QtGui.QFont("Arial", 10))
        self.label_fp_overall_firebase.setStyleSheet('color:green')
        self.label_fp_overall_firebase.setFixedHeight(20)
        self.label_fp_overall_firebase.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_fp_overall_firebase, 6, 0)

        self.label_fp_branch_firebase = QLabel("")
        self.label_fp_branch_firebase.setFont(QtGui.QFont("Arial", 10))
        self.label_fp_branch_firebase.setStyleSheet('color:green')
        self.label_fp_branch_firebase.setFixedHeight(20)
        self.label_fp_branch_firebase.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_fp_branch_firebase, 7, 0)

        self.label_fp_city_firebase = QLabel("")
        self.label_fp_city_firebase.setFont(QtGui.QFont("Arial", 10))
        self.label_fp_city_firebase.setStyleSheet('color:green')
        self.label_fp_city_firebase.setFixedHeight(20)
        self.label_fp_city_firebase.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_fp_city_firebase, 8, 0)

        self.labelAnimation = QLabel("")
        self.movie = QMovie('loading_3.gif')
        self.labelAnimation.setMovie(self.movie)
        gridLayout.addWidget(self.dummy_label,0,0)
        gridLayout.addWidget(self.labelAnimation,0,1)
        gridLayout.addWidget(self.dummy_label,0,2)
        self.movie.start()



        self.button_close = QPushButton("FINISH")
        self.button_close.setFont(QtGui.QFont("arial", 13))
        self.button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        self.button_close.setFixedWidth(150)
        self.button_close.setFixedHeight(60)
        self.button_close.setEnabled(False)
        self.button_close.clicked.connect(self.Close_Application)
        self.gridLayout2.addWidget(self.button_close, 9, 0)

        self.groupBox.setLayout(gridLayout)
        self.groupBox2.setLayout(self.gridLayout2)

        self.workerThread_1 = fpGrowth_Thread_for_Overall()
        self.workerThread_1.start()
        self.workerThread_1.finished.connect(self.update_Log_Overall)

        if(filter_dictionary['branch']==None):
            self.model_branch=False
        else:
            self.model_branch = True

        if(filter_dictionary['city']==None):
            self.model_city = False
        else:
            self.model_city = True



    def update_Log_Overall(self):
        print("fp growth overall done")
        self.label_fp_overall.setText("Fp Growth Overall Model 100% Completed")
        self.firebase_thread_1 = WriteResultForOverall()
        self.firebase_thread_1.start()
        self.firebase_thread_1.finished.connect(self.update_firebase_overall)

        if(filter_dictionary['branch']!=None):

            self.workerThread_2 = fpGrowth_Thread_for_Branch()
            self.workerThread_2.start()
            self.workerThread_2.finished.connect(self.update_Log_branch)


        elif(filter_dictionary['city']==None):


            self.workerThread_2 = fpGrowth_Thread_for_City()
            self.workerThread_2.start()
            self.workerThread_2.finished.connect(self.update_Log_city)


    def update_Log_branch(self):
        print('fp growth branch done')
        self.label_fp_branch.setText("Fp Growth Branch Model 100% Completed")
        self.firebase_thread_2 = WriteResultForBranch()
        self.firebase_thread_2.start()
        self.firebase_thread_2.finished.connect(self.update_firebase_branch)

        if(filter_dictionary['city']!=None):

            self.workerThread_2 = fpGrowth_Thread_for_City()
            self.workerThread_2.start()
            self.workerThread_2.finished.connect(self.update_Log_city)

    def update_Log_city(self):
        print('fp growth city done')
        self.label_fp_city.setText("Fp Growth City Model 100% Completed")
        self.firebase_thread_3 = WriteResultForCity()
        self.firebase_thread_3.start()
        self.firebase_thread_3.finished.connect(self.update_firebase_city)

    def Close_Application(self):
        sys.exit()

    def update_firebase_overall(self):
        self.overall_firebase = True
        self.label_fp_overall_firebase.setText("Overall results uploaded to Firebase 100%")

        if(self.model_branch==True and self.branch_firebase==False):
            pass

        elif(self.model_city==True and self.city_firebase==False):
            pass

        else:
            self.movie = QMovie('rsz_complete_534974.png')
            self.labelAnimation.setMovie(self.movie)
            self.movie.start()
            self.button_close.setStyleSheet('color:white;background-color:#003300')
            self.button_close.setEnabled(True)



    def update_firebase_city(self):
        self.city_firebase = True
        self.label_fp_city_firebase.setText("City results uploaded to Firebase 100%")

        if (self.model_branch == True and self.branch_firebase == False):
            pass

        elif (self.model_overall == True and self.overall_firebase == False):
            pass

        else:

            self.movie = QMovie('rsz_complete_534974.png')
            self.labelAnimation.setMovie(self.movie)
            self.movie.start()
            self.button_close.setStyleSheet('color:white;background-color:#003300')
            self.button_close.setEnabled(True)

    def update_firebase_branch(self):
        self.label_fp_branch_firebase.setText("Branch results uploaded to Firebase 100%")
        self.branch_firebase = True

        if (self.model_overall == True and self.overall_firebase == False):
            pass

        elif (self.model_city == True and self.city_firebase == False):
            pass

        else:
            self.movie = QMovie('rsz_complete_534974.png')
            self.labelAnimation.setMovie(self.movie)
            self.movie.start()
            self.button_close.setStyleSheet('color:white;background-color:#003300')
            self.button_close.setEnabled(True)

class Model_loading_Screen_customer(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Model Loading Customer"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.Init_Window()


    def Init_Window(self):
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.vbox.addWidget(self.groupBox2)
        self.setLayout(self.vbox)

        self.showMaximized()

    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox2 = QGroupBox("")

        self.groupBox.setStyleSheet('background-color:rgb(255,255,255)')
        self.groupBox2.setStyleSheet('background-color:rgb(255,255,255)')

        self.dummy_label = QLabel("")
        self.dummy_label.setMinimumHeight(20)
        self.dummy_label.setMinimumWidth(20)

        gridLayout = QGridLayout()
        self.gridLayout2 = QGridLayout()

        self.labelAnimation = QLabel("")
        self.movie = QMovie('loading_3.gif')
        self.labelAnimation.setMovie(self.movie)
        gridLayout.addWidget(self.dummy_label, 0, 0)
        gridLayout.addWidget(self.labelAnimation, 0, 1)
        gridLayout.addWidget(self.dummy_label, 0, 2)
        self.movie.start()

        self.label_log_1 = QLabel("Status: Preprocessing Data")
        self.label_log_1.setFont(QtGui.QFont("Arial", 10))
        self.label_log_1.setStyleSheet('color:green')
        self.label_log_1.setFixedHeight(20)
        self.label_log_1.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_1, 0, 1)

        self.label_log_2 = QLabel("Status: Preparing Model for prediction")
        self.label_log_2.setFont(QtGui.QFont("Arial", 10))
        self.label_log_2.setStyleSheet('color:green')
        self.label_log_2.setFixedHeight(20)
        self.label_log_2.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_2, 1, 1)

        self.label_log_3 = QLabel("Classifier Model: Random Forest Classifier")
        self.label_log_3.setFont(QtGui.QFont("Arial", 10))
        self.label_log_3.setStyleSheet('color:green')
        self.label_log_3.setFixedHeight(20)
        self.label_log_3.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_3, 2, 1)

        self.label_log_4 = QLabel("")
        self.label_log_4.setFont(QtGui.QFont("Arial", 10))
        self.label_log_4.setStyleSheet('color:green')
        self.label_log_4.setFixedHeight(20)
        self.label_log_4.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_4, 3, 1)

        self.label_log_5 = QLabel("")
        self.label_log_5.setFont(QtGui.QFont("Arial", 10))
        self.label_log_5.setStyleSheet('color:green')
        self.label_log_5.setFixedHeight(20)
        self.label_log_5.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_5, 4, 1)

        self.button_close = QPushButton("Proceed")
        self.button_close.setFont(QtGui.QFont("arial", 13))
        self.button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        self.button_close.setFixedWidth(150)
        self.button_close.setFixedHeight(60)
        self.button_close.setEnabled(False)
        self.button_close.clicked.connect(self.proceed_next)
        self.gridLayout2.addWidget(self.button_close, 9, 1)


        self.groupBox.setLayout(gridLayout)
        self.groupBox2.setLayout(self.gridLayout2)

        self.workerThread_1 = prepare_Model_for_chunk_prediction()
        self.workerThread_1.start()
        self.workerThread_1.finished.connect(self.updateStatus)

    def updateStatus(self):
        acc_str = "Model Accuracy: "+str(round(model_accuracy[0]*100))+" % "
        self.label_log_4.setText(acc_str)
        self.label_log_5.setText("Status: Model is ready for making predictions")
        self.movie = QMovie('rsz_complete_534974.png')
        self.labelAnimation.setMovie(self.movie)
        self.movie.start()
        self.button_close.setStyleSheet('color:white;background-color:#003300')
        self.button_close.setEnabled(True)


    def proceed_next(self):
        self.window = input_data_for_prediction()
        self.destroy()

class input_data_for_prediction(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "File selection for predictions"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.file_path = None


        self.Init_Window_1()

    def Init_Window_1(self):
        self.setWindowTitle(self.title)
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout_1()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.setLayout(self.vbox)
        self.showMaximized()

    def createLayout_1(self):

        self.groupBox = QGroupBox("")
        self.groupBox2 = QGroupBox("")
        self.groupBox2.setStyleSheet('background-color:white')
        self.groupBox.setStyleSheet('background-color:white')
        gridLayout = QGridLayout()
        gridLayout_2 = QGridLayout()

        self.dummylabel_1 = QLabel("")
        self.setMinimumHeight(40)
        self.setMinimumWidth(40)

        self.File_search_logo = QLabel("")
        pixmap = QPixmap("File_search.png")
        self.File_search_logo.setPixmap(pixmap)
        self.File_search_logo.setFixedHeight(450)
        self.File_search_logo.setFixedWidth(450)



        self.label = QLabel("Select file for making predictions.\nYour file must be in csv format.")
        self.label.setFont(QtGui.QFont("Arial", 20))
        self.label.setStyleSheet('color:black')
        self.label.setMinimumWidth(5)
        self.label.setMinimumHeight(40)
        gridLayout.addWidget(self.label, 0, 0)
        gridLayout.addWidget(self.groupBox2,2,5)
        gridLayout.addWidget(self.dummylabel_1, 2, 0)
        gridLayout.addWidget(self.dummylabel_1, 2, 1)
        gridLayout.addWidget(self.dummylabel_1, 2, 3)
        gridLayout.addWidget(self.dummylabel_1, 2, 4)
        gridLayout_2.addWidget(self.File_search_logo,0,0)


        gridLayout.addWidget(self.dummylabel_1, 3, 0)
        gridLayout.addWidget(self.dummylabel_1, 4, 0)

        button = QPushButton("Browse File")
        button.setIcon(QtGui.QIcon("search_icon.png"))
        button.setIconSize(QtCore.QSize(70, 70))
        button.setFont(QtGui.QFont("Arial", 15))
        button.setStyleSheet('color:white; background-color:rgb(128, 128, 128)')
        button.setFixedWidth(270)
        button.setFixedHeight(120)
        button.clicked.connect(self.file_open_for_processing)
        gridLayout.addWidget(button, 2,1)

        button = QPushButton("Next")
        button.setFont(QtGui.QFont("arial", 15))
        button.setStyleSheet('color:white; background-color:#003300')
        button.setFixedWidth(150)
        button.setFixedHeight(60)
        button.clicked.connect(self.Click_Next_btn_1)
        gridLayout.addWidget(button, 5, 6)

        button_close = QPushButton("Back")
        button_close.setFont(QtGui.QFont("arial", 15))
        button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        button_close.setFixedWidth(150)
        button_close.setFixedHeight(60)
        button_close.clicked.connect(self.Close_Application_1)
        gridLayout.addWidget(button_close, 5, 0)

        self.groupBox.setLayout(gridLayout)
        self.groupBox2.setLayout(gridLayout_2)


    def file_open_for_processing(self):
        self.file_path = None
        pathList_2.clear()
        self.file_path =QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')


    def Close_Application_1(self):
        sys.exit()

    def Click_Next_btn_1(self):

        if(self.file_path!=None and self.file_path[0]!=""):
            pathList_2.append(self.file_path[0])
            print(pathList_2)
            self.window = predictions_loading_screen()
            self.destroy()

class predictions_loading_screen(QDialog):

    def __init__(self):
        super().__init__()
        self.title = "Prediction Loading Screen"
        self.top = 500
        self.left = 200
        self.width = 300
        self.height = 250
        self.Init_Window()


    def Init_Window(self):
        self.setStyleSheet('background-color:rgb(105,105,105)')
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.createLayout()
        self.vbox = QVBoxLayout()
        self.TitleLabel = QLabel(" TRENDICA ")
        self.TitleLabel.setFont(QtGui.QFont("Arial", 34))
        self.TitleLabel.setStyleSheet('color:white; background-color:#33CCFF; font-weight: bold')
        self.TitleLabel.setMaximumWidth(10000)
        self.TitleLabel.setMaximumHeight(50)
        self.vbox.addWidget(self.TitleLabel)
        self.vbox.addWidget(self.groupBox)
        self.vbox.addWidget(self.groupBox2)
        self.setLayout(self.vbox)

        self.showMaximized()

    def createLayout(self):
        self.groupBox = QGroupBox("")
        self.groupBox2 = QGroupBox("")

        self.groupBox.setStyleSheet('background-color:rgb(255,255,255)')
        self.groupBox2.setStyleSheet('background-color:rgb(255,255,255)')

        self.dummy_label = QLabel("")
        self.dummy_label.setMinimumHeight(20)
        self.dummy_label.setMinimumWidth(20)

        gridLayout = QGridLayout()
        self.gridLayout2 = QGridLayout()

        self.labelAnimation = QLabel("")
        self.movie = QMovie('loading_3.gif')
        self.labelAnimation.setMovie(self.movie)
        gridLayout.addWidget(self.dummy_label, 0, 0)
        gridLayout.addWidget(self.labelAnimation, 0, 1)
        gridLayout.addWidget(self.dummy_label, 0, 2)
        self.movie.start()

        self.label_log_1 = QLabel("Status: Preprocessing Data")
        self.label_log_1.setFont(QtGui.QFont("Arial", 10))
        self.label_log_1.setStyleSheet('color:green')
        self.label_log_1.setFixedHeight(20)
        self.label_log_1.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_1, 0, 1)

        self.label_log_2 = QLabel("Status: Preparing data for prediction")
        self.label_log_2.setFont(QtGui.QFont("Arial", 10))
        self.label_log_2.setStyleSheet('color:green')
        self.label_log_2.setFixedHeight(20)
        self.label_log_2.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_2, 1, 1)

        self.label_log_3 = QLabel("Classifier Model: Random Forest Classifier")
        self.label_log_3.setFont(QtGui.QFont("Arial", 10))
        self.label_log_3.setStyleSheet('color:green')
        self.label_log_3.setFixedHeight(20)
        self.label_log_3.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_3, 2, 1)

        self.label_log_4 = QLabel("")
        self.label_log_4.setFont(QtGui.QFont("Arial", 10))
        self.label_log_4.setStyleSheet('color:green')
        self.label_log_4.setFixedHeight(20)
        self.label_log_4.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_4, 3, 1)

        self.label_log_5 = QLabel("")
        self.label_log_5.setFont(QtGui.QFont("Arial", 10))
        self.label_log_5.setStyleSheet('color:green')
        self.label_log_5.setFixedHeight(20)
        self.label_log_5.setFixedWidth(300)
        self.gridLayout2.addWidget(self.label_log_5, 4, 1)

        self.button_close = QPushButton("Proceed")
        self.button_close.setFont(QtGui.QFont("arial", 13))
        self.button_close.setStyleSheet('color:white; background-color:rgb(96,0,0)')
        self.button_close.setFixedWidth(150)
        self.button_close.setFixedHeight(60)
        self.button_close.setEnabled(False)
        self.button_close.clicked.connect(self.closeApp)
        self.gridLayout2.addWidget(self.button_close, 9, 1)


        self.groupBox.setLayout(gridLayout)
        self.groupBox2.setLayout(self.gridLayout2)

        self.workerThread_1 = make_predictions()
        self.workerThread_1.start()
        self.workerThread_1.finished.connect(self.updateStatus)


    def updateStatus(self):

        if(out_dict_customer[0][0]==True):

            msg_box = QMessageBox()
            msg_box.setMinimumHeight(100)
            msg_box.setMinimumWidth(100)
            msg_box.setWindowTitle("Error")
            msg_box.setText(out_dict_customer[0][1])
            msg_box.setIcon(QMessageBox.Information)
            x = msg_box.exec_()

        else:
            self.label_log_4.setText("Predictions Status: Done")
            self.label_log_5.setText("Uploading Data.../")
            self.workerThread_2 = upload_customer_predictions()
            self.workerThread_2.start()
            self.workerThread_2.finished.connect(self.proceed_next)



    def proceed_next(self):
        self.movie = QMovie('rsz_complete_534974.png')
        self.labelAnimation.setMovie(self.movie)
        self.movie.start()
        self.button_close.setStyleSheet('color:white;background-color:#003300')
        self.button_close.setEnabled(True)

    def closeApp(self):
        sys.exit()

App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())