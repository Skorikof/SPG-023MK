# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_amortpoNFKt.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QComboBox, QFrame, QLabel,
                               QLineEdit, QPushButton, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(690, 580)
        MainWindow.setMinimumSize(QSize(690, 580))
        MainWindow.setMaximumSize(QSize(690, 580))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame_parameters = QFrame(self.centralwidget)
        self.frame_parameters.setObjectName(u"frame_parameters")
        self.frame_parameters.setGeometry(QRect(5, 5, 680, 520))
        self.frame_parameters.setFrameShape(QFrame.Box)
        self.frame_parameters.setFrameShadow(QFrame.Raised)
        self.frame_parameters.setLineWidth(2)
        self.lbl_txt9 = QLabel(self.frame_parameters)
        self.lbl_txt9.setObjectName(u"lbl_txt9")
        self.lbl_txt9.setGeometry(QRect(20, 470, 400, 35))
        font = QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(18)
        font.setBold(True)
        self.lbl_txt9.setFont(font)
        self.lbl_txt9.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt9.setFrameShape(QFrame.NoFrame)
        self.lbl_txt9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt5 = QLabel(self.frame_parameters)
        self.lbl_txt5.setObjectName(u"lbl_txt5")
        self.lbl_txt5.setGeometry(QRect(20, 380, 400, 35))
        self.lbl_txt5.setFont(font)
        self.lbl_txt5.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt5.setFrameShape(QFrame.NoFrame)
        self.lbl_txt5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt4 = QLabel(self.frame_parameters)
        self.lbl_txt4.setObjectName(u"lbl_txt4")
        self.lbl_txt4.setGeometry(QRect(20, 65, 400, 35))
        self.lbl_txt4.setFont(font)
        self.lbl_txt4.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt6 = QLabel(self.frame_parameters)
        self.lbl_txt6.setObjectName(u"lbl_txt6")
        self.lbl_txt6.setGeometry(QRect(20, 290, 400, 35))
        self.lbl_txt6.setFont(font)
        self.lbl_txt6.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt6.setFrameShape(QFrame.NoFrame)
        self.lbl_txt6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt4_2 = QLabel(self.frame_parameters)
        self.lbl_txt4_2.setObjectName(u"lbl_txt4_2")
        self.lbl_txt4_2.setGeometry(QRect(20, 110, 400, 35))
        self.lbl_txt4_2.setFont(font)
        self.lbl_txt4_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_2.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt5_2 = QLabel(self.frame_parameters)
        self.lbl_txt5_2.setObjectName(u"lbl_txt5_2")
        self.lbl_txt5_2.setGeometry(QRect(20, 425, 400, 35))
        self.lbl_txt5_2.setFont(font)
        self.lbl_txt5_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt5_2.setFrameShape(QFrame.NoFrame)
        self.lbl_txt5_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt6_2 = QLabel(self.frame_parameters)
        self.lbl_txt6_2.setObjectName(u"lbl_txt6_2")
        self.lbl_txt6_2.setGeometry(QRect(20, 335, 400, 35))
        self.lbl_txt6_2.setFont(font)
        self.lbl_txt6_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt6_2.setFrameShape(QFrame.NoFrame)
        self.lbl_txt6_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt4_3 = QLabel(self.frame_parameters)
        self.lbl_txt4_3.setObjectName(u"lbl_txt4_3")
        self.lbl_txt4_3.setGeometry(QRect(20, 155, 400, 35))
        self.lbl_txt4_3.setFont(font)
        self.lbl_txt4_3.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_3.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt4_4 = QLabel(self.frame_parameters)
        self.lbl_txt4_4.setObjectName(u"lbl_txt4_4")
        self.lbl_txt4_4.setGeometry(QRect(20, 245, 400, 35))
        self.lbl_txt4_4.setFont(font)
        self.lbl_txt4_4.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_4.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_name = QLineEdit(self.frame_parameters)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setGeometry(QRect(20, 15, 640, 40))
        self.lineEdit_name.setFont(font)
        self.le_length_min = QLineEdit(self.frame_parameters)
        self.le_length_min.setObjectName(u"le_length_min")
        self.le_length_min.setGeometry(QRect(490, 65, 110, 35))
        self.le_length_min.setFont(font)
        self.le_length_min.setAlignment(Qt.AlignCenter)
        self.le_length_max = QLineEdit(self.frame_parameters)
        self.le_length_max.setObjectName(u"le_length_max")
        self.le_length_max.setGeometry(QRect(490, 110, 110, 35))
        self.le_length_max.setFont(font)
        self.le_length_max.setAlignment(Qt.AlignCenter)
        self.le_hod = QLineEdit(self.frame_parameters)
        self.le_hod.setObjectName(u"le_hod")
        self.le_hod.setGeometry(QRect(490, 155, 110, 35))
        self.le_hod.setFont(font)
        self.le_hod.setAlignment(Qt.AlignCenter)
        self.le_speed_one = QLineEdit(self.frame_parameters)
        self.le_speed_one.setObjectName(u"le_speed_one")
        self.le_speed_one.setGeometry(QRect(440, 245, 110, 35))
        self.le_speed_one.setFont(font)
        self.le_speed_one.setAlignment(Qt.AlignCenter)
        self.le_speed_two = QLineEdit(self.frame_parameters)
        self.le_speed_two.setObjectName(u"le_speed_two")
        self.le_speed_two.setGeometry(QRect(560, 245, 110, 35))
        self.le_speed_two.setFont(font)
        self.le_speed_two.setAlignment(Qt.AlignCenter)
        self.le_comp_min = QLineEdit(self.frame_parameters)
        self.le_comp_min.setObjectName(u"le_comp_min")
        self.le_comp_min.setGeometry(QRect(440, 380, 110, 35))
        self.le_comp_min.setFont(font)
        self.le_comp_min.setAlignment(Qt.AlignCenter)
        self.le_comp_max = QLineEdit(self.frame_parameters)
        self.le_comp_max.setObjectName(u"le_comp_max")
        self.le_comp_max.setGeometry(QRect(440, 425, 110, 35))
        self.le_comp_max.setFont(font)
        self.le_comp_max.setAlignment(Qt.AlignCenter)
        self.le_recoil_min = QLineEdit(self.frame_parameters)
        self.le_recoil_min.setObjectName(u"le_recoil_min")
        self.le_recoil_min.setGeometry(QRect(440, 290, 110, 35))
        self.le_recoil_min.setFont(font)
        self.le_recoil_min.setAlignment(Qt.AlignCenter)
        self.le_recoil_max = QLineEdit(self.frame_parameters)
        self.le_recoil_max.setObjectName(u"le_recoil_max")
        self.le_recoil_max.setGeometry(QRect(440, 335, 110, 35))
        self.le_recoil_max.setFont(font)
        self.le_recoil_max.setAlignment(Qt.AlignCenter)
        self.le_temper = QLineEdit(self.frame_parameters)
        self.le_temper.setObjectName(u"le_temper")
        self.le_temper.setGeometry(QRect(490, 470, 110, 35))
        self.le_temper.setFont(font)
        self.le_temper.setAlignment(Qt.AlignCenter)
        self.lbl_txt4_6 = QLabel(self.frame_parameters)
        self.lbl_txt4_6.setObjectName(u"lbl_txt4_6")
        self.lbl_txt4_6.setGeometry(QRect(20, 200, 400, 35))
        self.lbl_txt4_6.setFont(font)
        self.lbl_txt4_6.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_6.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.adapter_cb = QComboBox(self.frame_parameters)
        self.adapter_cb.addItem("")
        self.adapter_cb.addItem("")
        self.adapter_cb.addItem("")
        self.adapter_cb.addItem("")
        self.adapter_cb.addItem("")
        self.adapter_cb.addItem("")
        self.adapter_cb.setObjectName(u"adapter_cb")
        self.adapter_cb.setGeometry(QRect(490, 200, 110, 35))
        self.adapter_cb.setFont(font)
        self.adapter_cb.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.le_comp_min_two = QLineEdit(self.frame_parameters)
        self.le_comp_min_two.setObjectName(u"le_comp_min_two")
        self.le_comp_min_two.setGeometry(QRect(560, 380, 110, 35))
        self.le_comp_min_two.setFont(font)
        self.le_comp_min_two.setAlignment(Qt.AlignCenter)
        self.le_comp_max_two = QLineEdit(self.frame_parameters)
        self.le_comp_max_two.setObjectName(u"le_comp_max_two")
        self.le_comp_max_two.setGeometry(QRect(560, 425, 110, 35))
        self.le_comp_max_two.setFont(font)
        self.le_comp_max_two.setAlignment(Qt.AlignCenter)
        self.le_recoil_min_two = QLineEdit(self.frame_parameters)
        self.le_recoil_min_two.setObjectName(u"le_recoil_min_two")
        self.le_recoil_min_two.setGeometry(QRect(560, 290, 110, 35))
        self.le_recoil_min_two.setFont(font)
        self.le_recoil_min_two.setAlignment(Qt.AlignCenter)
        self.le_recoil_max_two = QLineEdit(self.frame_parameters)
        self.le_recoil_max_two.setObjectName(u"le_recoil_max_two")
        self.le_recoil_max_two.setGeometry(QRect(560, 335, 110, 35))
        self.le_recoil_max_two.setFont(font)
        self.le_recoil_max_two.setAlignment(Qt.AlignCenter)
        self.btn_save = QPushButton(self.centralwidget)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setGeometry(QRect(480, 535, 140, 40))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(12)
        font1.setBold(True)
        self.btn_save.setFont(font1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0430\u043c\u043e\u0440\u0442\u0438\u0437\u0430\u0442\u043e\u0440\u0430", None))
        self.lbl_txt9.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 (\u2103)", None))
        self.lbl_txt5.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u0441\u0436\u0430\u0442\u0438\u044f (\u043a\u0433\u0441)", None))
        self.lbl_txt4.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043b\u0438\u043d\u0430 \u0432 \u0441\u0436\u0430\u0442\u043e\u043c \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0438 (\u043c\u043c)", None))
        self.lbl_txt6.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u043e\u0442\u0431\u043e\u044f (\u043a\u0433\u0441)", None))
        self.lbl_txt4_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043b\u0438\u043d\u0430 \u0432 \u0440\u0430\u0441\u0442\u044f\u043d\u0443\u0442\u043e\u043c \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0438 (\u043c\u043c)", None))
        self.lbl_txt5_2.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u0441\u0436\u0430\u0442\u0438\u044f (\u043a\u0433\u0441)", None))
        self.lbl_txt6_2.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0443\u0441\u0438\u043b\u0438\u0435 \u043e\u0442\u0431\u043e\u044f (\u043a\u0433\u0441)", None))
        self.lbl_txt4_3.setText(QCoreApplication.translate("MainWindow", u"\u0425\u043e\u0434 (\u043c\u043c)", None))
        self.lbl_txt4_4.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f (\u043c/\u0441)", None))
        self.lineEdit_name.setText("")
        self.le_length_min.setText("")
        self.le_length_max.setText("")
        self.le_hod.setText("")
        self.le_speed_one.setText("")
        self.le_speed_two.setText("")
        self.le_comp_min.setText("")
        self.le_comp_max.setText("")
        self.le_recoil_min.setText("")
        self.le_recoil_max.setText("")
        self.le_temper.setText("")
        self.lbl_txt4_6.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0434\u0430\u043f\u0442\u0435\u0440 (\u2116)", None))
        self.adapter_cb.setItemText(0, QCoreApplication.translate("MainWindow", u"069", None))
        self.adapter_cb.setItemText(1, QCoreApplication.translate("MainWindow", u"069-01", None))
        self.adapter_cb.setItemText(2, QCoreApplication.translate("MainWindow", u"069-02", None))
        self.adapter_cb.setItemText(3, QCoreApplication.translate("MainWindow", u"069-03", None))
        self.adapter_cb.setItemText(4, QCoreApplication.translate("MainWindow", u"069-04", None))
        self.adapter_cb.setItemText(5, QCoreApplication.translate("MainWindow", u"072", None))

        self.le_comp_min_two.setText("")
        self.le_comp_max_two.setText("")
        self.le_recoil_min_two.setText("")
        self.le_recoil_max_two.setText("")
        self.btn_save.setText(QCoreApplication.translate("MainWindow", u"\u0421\u041e\u0425\u0420\u0410\u041d\u0418\u0422\u042c", None))
    # retranslateUi

