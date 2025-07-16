# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'amorts_uiLdBgWy.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QWidget)

class Ui_AmortsWindow(object):
    def setupUi(self, AmortsWindow):
        if not AmortsWindow.objectName():
            AmortsWindow.setObjectName(u"AmortsWindow")
        AmortsWindow.resize(645, 665)
        AmortsWindow.setMinimumSize(QSize(645, 665))
        AmortsWindow.setMaximumSize(QSize(645, 665))
        self.centralwidget = QWidget(AmortsWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame_parameters = QFrame(self.centralwidget)
        self.frame_parameters.setObjectName(u"frame_parameters")
        self.frame_parameters.setGeometry(QRect(15, 10, 615, 560))
        self.frame_parameters.setFrameShape(QFrame.Box)
        self.frame_parameters.setFrameShadow(QFrame.Raised)
        self.frame_parameters.setLineWidth(2)
        self.lbl_comp_max = QLabel(self.frame_parameters)
        self.lbl_comp_max.setObjectName(u"lbl_comp_max")
        self.lbl_comp_max.setGeometry(QRect(370, 465, 110, 35))
        font = QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(18)
        font.setBold(True)
        self.lbl_comp_max.setFont(font)
        self.lbl_comp_max.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_comp_max.setFrameShape(QFrame.Box)
        self.lbl_comp_max.setAlignment(Qt.AlignCenter)
        self.lbl_txt9 = QLabel(self.frame_parameters)
        self.lbl_txt9.setObjectName(u"lbl_txt9")
        self.lbl_txt9.setGeometry(QRect(20, 510, 340, 35))
        font1 = QFont()
        font1.setFamilies([u"Calibri"])
        font1.setPointSize(16)
        font1.setBold(False)
        self.lbl_txt9.setFont(font1)
        self.lbl_txt9.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt9.setFrameShape(QFrame.NoFrame)
        self.lbl_txt9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt5 = QLabel(self.frame_parameters)
        self.lbl_txt5.setObjectName(u"lbl_txt5")
        self.lbl_txt5.setGeometry(QRect(20, 420, 340, 35))
        self.lbl_txt5.setFont(font1)
        self.lbl_txt5.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt5.setFrameShape(QFrame.NoFrame)
        self.lbl_txt5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_recoil_min = QLabel(self.frame_parameters)
        self.lbl_recoil_min.setObjectName(u"lbl_recoil_min")
        self.lbl_recoil_min.setGeometry(QRect(370, 330, 110, 35))
        self.lbl_recoil_min.setFont(font)
        self.lbl_recoil_min.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_recoil_min.setFrameShape(QFrame.Box)
        self.lbl_recoil_min.setAlignment(Qt.AlignCenter)
        self.lbl_txt3 = QLabel(self.frame_parameters)
        self.lbl_txt3.setObjectName(u"lbl_txt3")
        self.lbl_txt3.setGeometry(QRect(20, 65, 575, 30))
        self.lbl_txt3.setFont(font1)
        self.lbl_txt3.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt3.setFrameShape(QFrame.Box)
        self.lbl_txt3.setAlignment(Qt.AlignCenter)
        self.lbl_length_min = QLabel(self.frame_parameters)
        self.lbl_length_min.setObjectName(u"lbl_length_min")
        self.lbl_length_min.setGeometry(QRect(430, 105, 110, 35))
        self.lbl_length_min.setFont(font)
        self.lbl_length_min.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_length_min.setFrameShape(QFrame.Box)
        self.lbl_length_min.setAlignment(Qt.AlignCenter)
        self.lbl_temper = QLabel(self.frame_parameters)
        self.lbl_temper.setObjectName(u"lbl_temper")
        self.lbl_temper.setGeometry(QRect(430, 510, 110, 35))
        self.lbl_temper.setFont(font)
        self.lbl_temper.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_temper.setFrameShape(QFrame.Box)
        self.lbl_temper.setAlignment(Qt.AlignCenter)
        self.lbl_length_max = QLabel(self.frame_parameters)
        self.lbl_length_max.setObjectName(u"lbl_length_max")
        self.lbl_length_max.setGeometry(QRect(430, 150, 110, 35))
        self.lbl_length_max.setFont(font)
        self.lbl_length_max.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_length_max.setFrameShape(QFrame.Box)
        self.lbl_length_max.setAlignment(Qt.AlignCenter)
        self.lbl_txt4 = QLabel(self.frame_parameters)
        self.lbl_txt4.setObjectName(u"lbl_txt4")
        self.lbl_txt4.setGeometry(QRect(20, 105, 340, 35))
        self.lbl_txt4.setFont(font1)
        self.lbl_txt4.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt6 = QLabel(self.frame_parameters)
        self.lbl_txt6.setObjectName(u"lbl_txt6")
        self.lbl_txt6.setGeometry(QRect(20, 330, 340, 35))
        self.lbl_txt6.setFont(font1)
        self.lbl_txt6.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt6.setFrameShape(QFrame.NoFrame)
        self.lbl_txt6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_comp_min = QLabel(self.frame_parameters)
        self.lbl_comp_min.setObjectName(u"lbl_comp_min")
        self.lbl_comp_min.setGeometry(QRect(370, 420, 110, 35))
        self.lbl_comp_min.setFont(font)
        self.lbl_comp_min.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_comp_min.setFrameShape(QFrame.Box)
        self.lbl_comp_min.setAlignment(Qt.AlignCenter)
        self.lbl_recoil_max = QLabel(self.frame_parameters)
        self.lbl_recoil_max.setObjectName(u"lbl_recoil_max")
        self.lbl_recoil_max.setGeometry(QRect(370, 375, 110, 35))
        self.lbl_recoil_max.setFont(font)
        self.lbl_recoil_max.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_recoil_max.setFrameShape(QFrame.Box)
        self.lbl_recoil_max.setAlignment(Qt.AlignCenter)
        self.combo_Names = QComboBox(self.frame_parameters)
        self.combo_Names.setObjectName(u"combo_Names")
        self.combo_Names.setGeometry(QRect(20, 14, 575, 40))
        self.combo_Names.setMinimumSize(QSize(0, 40))
        self.combo_Names.setMaximumSize(QSize(16777215, 40))
        self.combo_Names.setFont(font)
        self.combo_Names.setStyleSheet(u"background-color: rgb(255, 255, 127);")
        self.combo_Names.setEditable(False)
        self.lbl_txt4_2 = QLabel(self.frame_parameters)
        self.lbl_txt4_2.setObjectName(u"lbl_txt4_2")
        self.lbl_txt4_2.setGeometry(QRect(20, 150, 340, 35))
        self.lbl_txt4_2.setFont(font1)
        self.lbl_txt4_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_2.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt5_2 = QLabel(self.frame_parameters)
        self.lbl_txt5_2.setObjectName(u"lbl_txt5_2")
        self.lbl_txt5_2.setGeometry(QRect(20, 465, 340, 35))
        self.lbl_txt5_2.setFont(font1)
        self.lbl_txt5_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt5_2.setFrameShape(QFrame.NoFrame)
        self.lbl_txt5_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt6_2 = QLabel(self.frame_parameters)
        self.lbl_txt6_2.setObjectName(u"lbl_txt6_2")
        self.lbl_txt6_2.setGeometry(QRect(20, 375, 340, 35))
        self.lbl_txt6_2.setFont(font1)
        self.lbl_txt6_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt6_2.setFrameShape(QFrame.NoFrame)
        self.lbl_txt6_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt4_3 = QLabel(self.frame_parameters)
        self.lbl_txt4_3.setObjectName(u"lbl_txt4_3")
        self.lbl_txt4_3.setGeometry(QRect(20, 195, 340, 35))
        self.lbl_txt4_3.setFont(font1)
        self.lbl_txt4_3.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_3.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_hod = QLabel(self.frame_parameters)
        self.lbl_hod.setObjectName(u"lbl_hod")
        self.lbl_hod.setGeometry(QRect(430, 195, 110, 35))
        self.lbl_hod.setFont(font)
        self.lbl_hod.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_hod.setFrameShape(QFrame.Box)
        self.lbl_hod.setAlignment(Qt.AlignCenter)
        self.lbl_txt4_4 = QLabel(self.frame_parameters)
        self.lbl_txt4_4.setObjectName(u"lbl_txt4_4")
        self.lbl_txt4_4.setGeometry(QRect(20, 285, 340, 35))
        self.lbl_txt4_4.setFont(font1)
        self.lbl_txt4_4.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_4.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_speed_1 = QLabel(self.frame_parameters)
        self.lbl_speed_1.setObjectName(u"lbl_speed_1")
        self.lbl_speed_1.setGeometry(QRect(370, 285, 110, 35))
        self.lbl_speed_1.setFont(font)
        self.lbl_speed_1.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_speed_1.setFrameShape(QFrame.Box)
        self.lbl_speed_1.setAlignment(Qt.AlignCenter)
        self.lbl_txt4_6 = QLabel(self.frame_parameters)
        self.lbl_txt4_6.setObjectName(u"lbl_txt4_6")
        self.lbl_txt4_6.setGeometry(QRect(20, 240, 340, 35))
        self.lbl_txt4_6.setFont(font1)
        self.lbl_txt4_6.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt4_6.setFrameShape(QFrame.NoFrame)
        self.lbl_txt4_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_adapter = QLabel(self.frame_parameters)
        self.lbl_adapter.setObjectName(u"lbl_adapter")
        self.lbl_adapter.setGeometry(QRect(430, 240, 110, 35))
        self.lbl_adapter.setFont(font)
        self.lbl_adapter.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_adapter.setFrameShape(QFrame.Box)
        self.lbl_adapter.setAlignment(Qt.AlignCenter)
        self.lbl_speed_2 = QLabel(self.frame_parameters)
        self.lbl_speed_2.setObjectName(u"lbl_speed_2")
        self.lbl_speed_2.setGeometry(QRect(490, 285, 110, 35))
        self.lbl_speed_2.setFont(font)
        self.lbl_speed_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_speed_2.setFrameShape(QFrame.Box)
        self.lbl_speed_2.setAlignment(Qt.AlignCenter)
        self.lbl_comp_min_2 = QLabel(self.frame_parameters)
        self.lbl_comp_min_2.setObjectName(u"lbl_comp_min_2")
        self.lbl_comp_min_2.setGeometry(QRect(490, 420, 110, 35))
        self.lbl_comp_min_2.setFont(font)
        self.lbl_comp_min_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_comp_min_2.setFrameShape(QFrame.Box)
        self.lbl_comp_min_2.setAlignment(Qt.AlignCenter)
        self.lbl_comp_max_2 = QLabel(self.frame_parameters)
        self.lbl_comp_max_2.setObjectName(u"lbl_comp_max_2")
        self.lbl_comp_max_2.setGeometry(QRect(490, 465, 110, 35))
        self.lbl_comp_max_2.setFont(font)
        self.lbl_comp_max_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_comp_max_2.setFrameShape(QFrame.Box)
        self.lbl_comp_max_2.setAlignment(Qt.AlignCenter)
        self.lbl_recoil_min_2 = QLabel(self.frame_parameters)
        self.lbl_recoil_min_2.setObjectName(u"lbl_recoil_min_2")
        self.lbl_recoil_min_2.setGeometry(QRect(490, 330, 110, 35))
        self.lbl_recoil_min_2.setFont(font)
        self.lbl_recoil_min_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_recoil_min_2.setFrameShape(QFrame.Box)
        self.lbl_recoil_min_2.setAlignment(Qt.AlignCenter)
        self.lbl_recoil_max_2 = QLabel(self.frame_parameters)
        self.lbl_recoil_max_2.setObjectName(u"lbl_recoil_max_2")
        self.lbl_recoil_max_2.setGeometry(QRect(490, 375, 110, 35))
        self.lbl_recoil_max_2.setFont(font)
        self.lbl_recoil_max_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_recoil_max_2.setFrameShape(QFrame.Box)
        self.lbl_recoil_max_2.setAlignment(Qt.AlignCenter)
        self.frame_btn = QFrame(self.centralwidget)
        self.frame_btn.setObjectName(u"frame_btn")
        self.frame_btn.setGeometry(QRect(15, 567, 615, 80))
        self.frame_btn.setMinimumSize(QSize(615, 80))
        self.frame_btn.setMaximumSize(QSize(615, 80))
        self.frame_btn.setFrameShape(QFrame.Box)
        self.frame_btn.setFrameShadow(QFrame.Raised)
        self.frame_btn.setLineWidth(2)
        self.horizontalLayout = QHBoxLayout(self.frame_btn)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.btn_add = QPushButton(self.frame_btn)
        self.btn_add.setObjectName(u"btn_add")
        self.btn_add.setMinimumSize(QSize(140, 40))
        self.btn_add.setMaximumSize(QSize(140, 40))
        font2 = QFont()
        font2.setFamilies([u"Calibri"])
        font2.setPointSize(18)
        font2.setBold(False)
        self.btn_add.setFont(font2)
        self.btn_add.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}")

        self.horizontalLayout.addWidget(self.btn_add)

        self.btn_change = QPushButton(self.frame_btn)
        self.btn_change.setObjectName(u"btn_change")
        self.btn_change.setMinimumSize(QSize(140, 40))
        self.btn_change.setMaximumSize(QSize(140, 40))
        self.btn_change.setFont(font2)
        self.btn_change.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}")

        self.horizontalLayout.addWidget(self.btn_change)

        self.btn_del = QPushButton(self.frame_btn)
        self.btn_del.setObjectName(u"btn_del")
        self.btn_del.setMinimumSize(QSize(140, 40))
        self.btn_del.setMaximumSize(QSize(140, 40))
        self.btn_del.setFont(font2)
        self.btn_del.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}")

        self.horizontalLayout.addWidget(self.btn_del)

        self.btn_exit = QPushButton(self.frame_btn)
        self.btn_exit.setObjectName(u"btn_exit")
        self.btn_exit.setMinimumSize(QSize(140, 40))
        self.btn_exit.setMaximumSize(QSize(140, 40))
        self.btn_exit.setFont(font2)
        self.btn_exit.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}")

        self.horizontalLayout.addWidget(self.btn_exit)

        self.frame_quest = QFrame(self.centralwidget)
        self.frame_quest.setObjectName(u"frame_quest")
        self.frame_quest.setGeometry(QRect(610, -160, 555, 251))
        self.frame_quest.setStyleSheet(u"background-color: rgb(85, 170, 127);")
        self.frame_quest.setFrameShape(QFrame.Box)
        self.frame_quest.setFrameShadow(QFrame.Raised)
        self.frame_quest.setLineWidth(2)
        self.txt_quest = QTextEdit(self.frame_quest)
        self.txt_quest.setObjectName(u"txt_quest")
        self.txt_quest.setGeometry(QRect(8, 14, 539, 155))
        font3 = QFont()
        font3.setFamilies([u"Calibri"])
        font3.setPointSize(20)
        font3.setBold(True)
        self.txt_quest.setFont(font3)
        self.txt_quest.setStyleSheet(u"")
        self.txt_quest.setFrameShape(QFrame.Box)
        self.txt_quest.setFrameShadow(QFrame.Plain)
        self.txt_quest.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_quest.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_quest.setReadOnly(True)
        self.btn_ok_quest = QPushButton(self.frame_quest)
        self.btn_ok_quest.setObjectName(u"btn_ok_quest")
        self.btn_ok_quest.setGeometry(QRect(150, 178, 73, 61))
        self.btn_ok_quest.setMinimumSize(QSize(30, 30))
        self.btn_ok_quest.setMaximumSize(QSize(400, 120))
        self.btn_ok_quest.setFont(font3)
        self.btn_ok_quest.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}")
        self.btn_cancel_quest = QPushButton(self.frame_quest)
        self.btn_cancel_quest.setObjectName(u"btn_cancel_quest")
        self.btn_cancel_quest.setGeometry(QRect(312, 178, 141, 57))
        self.btn_cancel_quest.setMinimumSize(QSize(30, 30))
        self.btn_cancel_quest.setMaximumSize(QSize(400, 120))
        self.btn_cancel_quest.setFont(font3)
        self.btn_cancel_quest.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}")
        self.frame_warning = QFrame(self.centralwidget)
        self.frame_warning.setObjectName(u"frame_warning")
        self.frame_warning.setGeometry(QRect(-530, -150, 555, 251))
        self.frame_warning.setStyleSheet(u"background-color: rgb(255, 170, 0);")
        self.frame_warning.setFrameShape(QFrame.Box)
        self.frame_warning.setFrameShadow(QFrame.Raised)
        self.frame_warning.setLineWidth(2)
        self.txt_warning = QTextEdit(self.frame_warning)
        self.txt_warning.setObjectName(u"txt_warning")
        self.txt_warning.setGeometry(QRect(8, 14, 539, 155))
        self.txt_warning.setFont(font3)
        self.txt_warning.setStyleSheet(u"")
        self.txt_warning.setFrameShape(QFrame.Box)
        self.txt_warning.setFrameShadow(QFrame.Plain)
        self.txt_warning.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_warning.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_warning.setReadOnly(True)
        self.btn_ok_warning = QPushButton(self.frame_warning)
        self.btn_ok_warning.setObjectName(u"btn_ok_warning")
        self.btn_ok_warning.setGeometry(QRect(240, 178, 73, 61))
        self.btn_ok_warning.setMinimumSize(QSize(30, 30))
        self.btn_ok_warning.setMaximumSize(QSize(400, 120))
        self.btn_ok_warning.setFont(font3)
        self.btn_ok_warning.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}")
        AmortsWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(AmortsWindow)

        QMetaObject.connectSlotsByName(AmortsWindow)
    # setupUi

    def retranslateUi(self, AmortsWindow):
        AmortsWindow.setWindowTitle(QCoreApplication.translate("AmortsWindow", u"\u0410\u043c\u043e\u0440\u0442\u0438\u0437\u0430\u0442\u043e\u0440\u044b", None))
        self.lbl_comp_max.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_txt9.setText(QCoreApplication.translate("AmortsWindow", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 (\u2103)", None))
        self.lbl_txt5.setText(QCoreApplication.translate("AmortsWindow", u"\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u0441\u0436\u0430\u0442\u0438\u044f (\u043a\u0433\u0441)", None))
        self.lbl_recoil_min.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_txt3.setText(QCoreApplication.translate("AmortsWindow", u"\u041f\u0410\u0420\u0410\u041c\u0415\u0422\u0420\u042b", None))
        self.lbl_length_min.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_temper.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_length_max.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_txt4.setText(QCoreApplication.translate("AmortsWindow", u"\u0414\u043b\u0438\u043d\u0430 \u0432 \u0441\u0436\u0430\u0442\u043e\u043c \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0438 (\u043c\u043c)", None))
        self.lbl_txt6.setText(QCoreApplication.translate("AmortsWindow", u"\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u043e\u0442\u0431\u043e\u044f (\u043a\u0433\u0441)", None))
        self.lbl_comp_min.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_recoil_max.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_txt4_2.setText(QCoreApplication.translate("AmortsWindow", u"\u0414\u043b\u0438\u043d\u0430 \u0432 \u0440\u0430\u0441\u0442\u044f\u043d\u0443\u0442\u043e\u043c \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0438 (\u043c\u043c)", None))
        self.lbl_txt5_2.setText(QCoreApplication.translate("AmortsWindow", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u0441\u0436\u0430\u0442\u0438\u044f (\u043a\u0433\u0441)", None))
        self.lbl_txt6_2.setText(QCoreApplication.translate("AmortsWindow", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0443\u0441\u0438\u043b\u0438\u0435 \u043e\u0442\u0431\u043e\u044f (\u043a\u0433\u0441)", None))
        self.lbl_txt4_3.setText(QCoreApplication.translate("AmortsWindow", u"\u0425\u043e\u0434 (\u043c\u043c)", None))
        self.lbl_hod.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_txt4_4.setText(QCoreApplication.translate("AmortsWindow", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f (\u043c/\u0441)", None))
        self.lbl_speed_1.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_txt4_6.setText(QCoreApplication.translate("AmortsWindow", u"\u0410\u0434\u0430\u043f\u0442\u0435\u0440 (\u2116)", None))
        self.lbl_adapter.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_speed_2.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_comp_min_2.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_comp_max_2.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_recoil_min_2.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.lbl_recoil_max_2.setText(QCoreApplication.translate("AmortsWindow", u"0", None))
        self.btn_add.setText(QCoreApplication.translate("AmortsWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.btn_change.setText(QCoreApplication.translate("AmortsWindow", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.btn_del.setText(QCoreApplication.translate("AmortsWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.btn_exit.setText(QCoreApplication.translate("AmortsWindow", u"\u0412\u044b\u0445\u043e\u0434", None))
        self.txt_quest.setMarkdown(QCoreApplication.translate("AmortsWindow", u"**\u0418\u041d\u0424\u041e\u0420\u041c\u0410\u0426\u0418\u042f**\n"
"\n"
"", None))
        self.txt_quest.setHtml(QCoreApplication.translate("AmortsWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Calibri'; font-size:20pt; font-weight:700; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:13px; margin-bottom:13px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">\u0418\u041d\u0424\u041e\u0420\u041c\u0410\u0426\u0418\u042f</span></p></body></html>", None))
        self.btn_ok_quest.setText(QCoreApplication.translate("AmortsWindow", u"Ok", None))
        self.btn_cancel_quest.setText(QCoreApplication.translate("AmortsWindow", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.txt_warning.setMarkdown(QCoreApplication.translate("AmortsWindow", u"**\u041f\u0420\u0415\u0414\u0423\u041f\u0420\u0415\u0416\u0414\u0415\u041d\u0418\u0415**\n"
"\n"
"", None))
        self.txt_warning.setHtml(QCoreApplication.translate("AmortsWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Calibri'; font-size:20pt; font-weight:700; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:13px; margin-bottom:13px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">\u041f\u0420\u0415\u0414\u0423\u041f\u0420\u0415\u0416\u0414\u0415\u041d\u0418\u0415</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:13px; margin-bottom:13px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p></body></html>", None))
        self.btn_ok_warning.setText(QCoreApplication.translate("AmortsWindow", u"Ok", None))
    # retranslateUi

