from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon, QPixmap

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowIcon(QIcon(QPixmap('logo.jpg')))
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(732, 532)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 701, 431))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.editButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.editButton.setGeometry(QtCore.QRect(50, 450, 131, 31))
        self.editButton.setObjectName("editButton")
        self.makeButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.makeButton.setGeometry(QtCore.QRect(280, 450, 141, 31))
        self.makeButton.setObjectName("makeButton")
        self.orderButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.orderButton.setGeometry(QtCore.QRect(560, 450, 141, 31))
        self.orderButton.setObjectName("orderButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 732, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.editButton.setText(_translate("MainWindow", "редактировать заказ"))
        self.makeButton.setText(_translate("MainWindow", "оформить заказ"))
        self.orderButton.setText(_translate("MainWindow", "мои заказы"))
