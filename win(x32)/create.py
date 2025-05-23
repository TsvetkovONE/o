from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon, QPixmap

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowIcon(QIcon(QPixmap('logo.jpg')))
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(799, 596)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 40, 781, 471))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.addButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.addButton.setGeometry(QtCore.QRect(30, 520, 131, 31))
        self.addButton.setObjectName("addButton")
        self.orderButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.orderButton.setGeometry(QtCore.QRect(180, 520, 121, 31))
        self.orderButton.setObjectName("orderButton")
        self.backButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.backButton.setGeometry(QtCore.QRect(650, 520, 121, 31))
        self.backButton.setObjectName("backButton")
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(570, 10, 221, 22))
        self.comboBox.setObjectName("comboBox")
        self.orderButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.orderButton_2.setGeometry(QtCore.QRect(490, 520, 141, 31))
        self.orderButton_2.setObjectName("orderButton_2")
        self.deleteButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.deleteButton.setGeometry(QtCore.QRect(330, 520, 121, 31))
        self.deleteButton.setObjectName("deleteButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 22))
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
        self.addButton.setText(_translate("MainWindow", "добавить товар"))
        self.orderButton.setText(_translate("MainWindow", "редактировать товар"))
        self.backButton.setText(_translate("MainWindow", "выход"))
        self.orderButton_2.setText(_translate("MainWindow", "посмотреть поставки"))
        self.deleteButton.setText(_translate("MainWindow", "удалить товар"))
