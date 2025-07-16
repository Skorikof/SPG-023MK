# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsUiAImKlH.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject,
                            QRect, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QFrame, QLCDNumber, QLabel,
                               QLineEdit, QPushButton,
                               QStatusBar, QWidget)

from modified_ui_obj.click_lineedit import MyLineEdit


class UiSettingsWindow(object):
    def setupUi(self, SettingsWindow):
        if not SettingsWindow.objectName():
            SettingsWindow.setObjectName(u"SettingsWindow")
        SettingsWindow.resize(610, 725)
        SettingsWindow.setMinimumSize(QSize(610, 725))
        SettingsWindow.setMaximumSize(QSize(610, 725))
        SettingsWindow.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.centralwidget = QWidget(SettingsWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.clear_force_lcd = QLCDNumber(self.centralwidget)
        self.clear_force_lcd.setObjectName(u"clear_force_lcd")
        self.clear_force_lcd.setGeometry(QRect(160, 54, 101, 43))
        self.clear_force_lcd.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.clear_force_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.clear_force_lcd.setProperty("value", -100.000000000000000)
        self.clear_force_lcd.setProperty("intValue", -100)
        self._lbl_txt2 = QLabel(self.centralwidget)
        self._lbl_txt2.setObjectName(u"_lbl_txt2")
        self._lbl_txt2.setGeometry(QRect(10, 58, 141, 32))
        font = QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(12)
        self._lbl_txt2.setFont(font)
        self._lbl_txt2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self._lbl_txt1 = QLabel(self.centralwidget)
        self._lbl_txt1.setObjectName(u"_lbl_txt1")
        self._lbl_txt1.setGeometry(QRect(38, 16, 113, 23))
        self._lbl_txt1.setFont(font)
        self._lbl_txt1.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lcdTime = QLCDNumber(self.centralwidget)
        self.lcdTime.setObjectName(u"lcdTime")
        self.lcdTime.setGeometry(QRect(160, 8, 101, 43))
        self.lcdTime.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.lcdTime.setSegmentStyle(QLCDNumber.Flat)
        self.lcdTime.setProperty("value", 0.000000000000000)
        self.lcdTime.setProperty("intValue", 0)
        self.fram_cycle_F = QLabel(self.centralwidget)
        self.fram_cycle_F.setObjectName(u"fram_cycle_F")
        self.fram_cycle_F.setGeometry(QRect(320, 12, 25, 25))
        self.fram_cycle_F.setMinimumSize(QSize(20, 20))
        self.fram_cycle_F.setMaximumSize(QSize(25, 25))
        self.fram_cycle_F.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_cycle_F.setFrameShape(QFrame.WinPanel)
        self.btn_cycle_F = QPushButton(self.centralwidget)
        self.btn_cycle_F.setObjectName(u"btn_cycle_F")
        self.btn_cycle_F.setGeometry(QRect(280, 10, 30, 30))
        self.btn_cycle_F.setMinimumSize(QSize(30, 30))
        self.btn_cycle_F.setMaximumSize(QSize(30, 30))
        self.btn_cycle_F.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_cycle_F.setCheckable(False)
        self.btn_cycle_F.setChecked(False)
        self._lbl_txt3 = QLabel(self.centralwidget)
        self._lbl_txt3.setObjectName(u"_lbl_txt3")
        self._lbl_txt3.setGeometry(QRect(350, 12, 243, 23))
        self._lbl_txt3.setFont(font)
        self._lbl_txt3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self._lbl_txt5 = QLabel(self.centralwidget)
        self._lbl_txt5.setObjectName(u"_lbl_txt5")
        self._lbl_txt5.setGeometry(QRect(350, 47, 243, 23))
        self._lbl_txt5.setFont(font)
        self._lbl_txt5.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt5.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_no_control = QLabel(self.centralwidget)
        self.fram_no_control.setObjectName(u"fram_no_control")
        self.fram_no_control.setGeometry(QRect(320, 47, 25, 25))
        self.fram_no_control.setMinimumSize(QSize(20, 20))
        self.fram_no_control.setMaximumSize(QSize(25, 25))
        self.fram_no_control.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_no_control.setFrameShape(QFrame.WinPanel)
        self.btn_no_control = QPushButton(self.centralwidget)
        self.btn_no_control.setObjectName(u"btn_no_control")
        self.btn_no_control.setGeometry(QRect(280, 45, 30, 30))
        self.btn_no_control.setMinimumSize(QSize(30, 30))
        self.btn_no_control.setMaximumSize(QSize(30, 30))
        self.btn_no_control.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_no_control.setCheckable(False)
        self.btn_no_control.setChecked(False)
        self.btn_max_F = QPushButton(self.centralwidget)
        self.btn_max_F.setObjectName(u"btn_max_F")
        self.btn_max_F.setGeometry(QRect(280, 80, 30, 30))
        self.btn_max_F.setMinimumSize(QSize(30, 30))
        self.btn_max_F.setMaximumSize(QSize(30, 30))
        self.btn_max_F.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_max_F.setCheckable(False)
        self.btn_max_F.setChecked(False)
        self.fram_max_F = QLabel(self.centralwidget)
        self.fram_max_F.setObjectName(u"fram_max_F")
        self.fram_max_F.setGeometry(QRect(320, 82, 25, 25))
        self.fram_max_F.setMinimumSize(QSize(20, 20))
        self.fram_max_F.setMaximumSize(QSize(25, 25))
        self.fram_max_F.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_max_F.setFrameShape(QFrame.WinPanel)
        self._lbl_txt6 = QLabel(self.centralwidget)
        self._lbl_txt6.setObjectName(u"_lbl_txt6")
        self._lbl_txt6.setGeometry(QRect(350, 82, 243, 23))
        self._lbl_txt6.setFont(font)
        self._lbl_txt6.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt6.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self._lbl_txt8 = QLabel(self.centralwidget)
        self._lbl_txt8.setObjectName(u"_lbl_txt8")
        self._lbl_txt8.setGeometry(QRect(350, 367, 243, 23))
        self._lbl_txt8.setFont(font)
        self._lbl_txt8.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt8.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_down_point = QLabel(self.centralwidget)
        self.fram_down_point.setObjectName(u"fram_down_point")
        self.fram_down_point.setGeometry(QRect(320, 367, 25, 25))
        self.fram_down_point.setMinimumSize(QSize(20, 20))
        self.fram_down_point.setMaximumSize(QSize(25, 25))
        self.fram_down_point.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_down_point.setFrameShape(QFrame.WinPanel)
        self.fram_up_point = QLabel(self.centralwidget)
        self.fram_up_point.setObjectName(u"fram_up_point")
        self.fram_up_point.setGeometry(QRect(320, 402, 25, 25))
        self.fram_up_point.setMinimumSize(QSize(20, 20))
        self.fram_up_point.setMaximumSize(QSize(25, 25))
        self.fram_up_point.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_up_point.setFrameShape(QFrame.WinPanel)
        self._lbl_txt9 = QLabel(self.centralwidget)
        self._lbl_txt9.setObjectName(u"_lbl_txt9")
        self._lbl_txt9.setGeometry(QRect(350, 402, 243, 23))
        self._lbl_txt9.setFont(font)
        self._lbl_txt9.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt9.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self._lbl_txt10 = QLabel(self.centralwidget)
        self._lbl_txt10.setObjectName(u"_lbl_txt10")
        self._lbl_txt10.setGeometry(QRect(350, 262, 243, 23))
        self._lbl_txt10.setFont(font)
        self._lbl_txt10.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt10.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_safety_fence = QLabel(self.centralwidget)
        self.fram_safety_fence.setObjectName(u"fram_safety_fence")
        self.fram_safety_fence.setGeometry(QRect(320, 262, 25, 25))
        self.fram_safety_fence.setMinimumSize(QSize(20, 20))
        self.fram_safety_fence.setMaximumSize(QSize(25, 25))
        self.fram_safety_fence.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_safety_fence.setFrameShape(QFrame.WinPanel)
        self.fram_condition_FC = QLabel(self.centralwidget)
        self.fram_condition_FC.setObjectName(u"fram_condition_FC")
        self.fram_condition_FC.setGeometry(QRect(320, 297, 25, 25))
        self.fram_condition_FC.setMinimumSize(QSize(20, 20))
        self.fram_condition_FC.setMaximumSize(QSize(25, 25))
        self.fram_condition_FC.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_condition_FC.setFrameShape(QFrame.WinPanel)
        self._lbl_txt11 = QLabel(self.centralwidget)
        self._lbl_txt11.setObjectName(u"_lbl_txt11")
        self._lbl_txt11.setGeometry(QRect(350, 297, 243, 23))
        self._lbl_txt11.setFont(font)
        self._lbl_txt11.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt11.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self._lbl_txt12 = QLabel(self.centralwidget)
        self._lbl_txt12.setObjectName(u"_lbl_txt12")
        self._lbl_txt12.setGeometry(QRect(350, 332, 243, 23))
        self._lbl_txt12.setFont(font)
        self._lbl_txt12.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt12.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_sensor_F = QLabel(self.centralwidget)
        self.fram_sensor_F.setObjectName(u"fram_sensor_F")
        self.fram_sensor_F.setGeometry(QRect(320, 332, 25, 25))
        self.fram_sensor_F.setMinimumSize(QSize(20, 20))
        self.fram_sensor_F.setMaximumSize(QSize(25, 25))
        self.fram_sensor_F.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_sensor_F.setFrameShape(QFrame.WinPanel)
        self._lbl_txt15 = QLabel(self.centralwidget)
        self._lbl_txt15.setObjectName(u"_lbl_txt15")
        self._lbl_txt15.setGeometry(QRect(10, 192, 143, 35))
        self._lbl_txt15.setFont(font)
        self._lbl_txt15.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt15.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lcdH = QLCDNumber(self.centralwidget)
        self.lcdH.setObjectName(u"lcdH")
        self.lcdH.setGeometry(QRect(160, 192, 101, 43))
        self.lcdH.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.lcdH.setSegmentStyle(QLCDNumber.Flat)
        self.lcdH.setProperty("value", 0.000000000000000)
        self.lcdH.setProperty("intValue", 0)
        self._lbl_txt15_2 = QLabel(self.centralwidget)
        self._lbl_txt15_2.setObjectName(u"_lbl_txt15_2")
        self._lbl_txt15_2.setGeometry(QRect(10, 285, 143, 35))
        font1 = QFont()
        font1.setFamilies([u"Calibri"])
        font1.setPointSize(11)
        self._lbl_txt15_2.setFont(font1)
        self._lbl_txt15_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt15_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lcdTemp_1 = QLCDNumber(self.centralwidget)
        self.lcdTemp_1.setObjectName(u"lcdTemp_1")
        self.lcdTemp_1.setGeometry(QRect(160, 284, 101, 43))
        self.lcdTemp_1.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.lcdTemp_1.setSegmentStyle(QLCDNumber.Flat)
        self.lcdTemp_1.setProperty("value", 0.000000000000000)
        self.lcdTemp_1.setProperty("intValue", 0)
        self.fram_block_traverse_1 = QLabel(self.centralwidget)
        self.fram_block_traverse_1.setObjectName(u"fram_block_traverse_1")
        self.fram_block_traverse_1.setGeometry(QRect(320, 437, 25, 25))
        self.fram_block_traverse_1.setMinimumSize(QSize(20, 20))
        self.fram_block_traverse_1.setMaximumSize(QSize(25, 25))
        self.fram_block_traverse_1.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_block_traverse_1.setFrameShape(QFrame.WinPanel)
        self._lbl_txt8_2 = QLabel(self.centralwidget)
        self._lbl_txt8_2.setObjectName(u"_lbl_txt8_2")
        self._lbl_txt8_2.setGeometry(QRect(350, 437, 243, 23))
        self._lbl_txt8_2.setFont(font)
        self._lbl_txt8_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt8_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_block_traverse_2 = QLabel(self.centralwidget)
        self.fram_block_traverse_2.setObjectName(u"fram_block_traverse_2")
        self.fram_block_traverse_2.setGeometry(QRect(320, 472, 25, 25))
        self.fram_block_traverse_2.setMinimumSize(QSize(20, 20))
        self.fram_block_traverse_2.setMaximumSize(QSize(25, 25))
        self.fram_block_traverse_2.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_block_traverse_2.setFrameShape(QFrame.WinPanel)
        self._lbl_txt9_2 = QLabel(self.centralwidget)
        self._lbl_txt9_2.setObjectName(u"_lbl_txt9_2")
        self._lbl_txt9_2.setGeometry(QRect(350, 472, 243, 23))
        self._lbl_txt9_2.setFont(font)
        self._lbl_txt9_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt9_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_down__alarm_point = QLabel(self.centralwidget)
        self.fram_down__alarm_point.setObjectName(u"fram_down__alarm_point")
        self.fram_down__alarm_point.setGeometry(QRect(320, 507, 25, 25))
        self.fram_down__alarm_point.setMinimumSize(QSize(20, 20))
        self.fram_down__alarm_point.setMaximumSize(QSize(25, 25))
        self.fram_down__alarm_point.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_down__alarm_point.setFrameShape(QFrame.WinPanel)
        self._lbl_txt8_3 = QLabel(self.centralwidget)
        self._lbl_txt8_3.setObjectName(u"_lbl_txt8_3")
        self._lbl_txt8_3.setGeometry(QRect(350, 503, 243, 31))
        self._lbl_txt8_3.setFont(font)
        self._lbl_txt8_3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt8_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_up_alarm_point = QLabel(self.centralwidget)
        self.fram_up_alarm_point.setObjectName(u"fram_up_alarm_point")
        self.fram_up_alarm_point.setGeometry(QRect(320, 542, 25, 25))
        self.fram_up_alarm_point.setMinimumSize(QSize(20, 20))
        self.fram_up_alarm_point.setMaximumSize(QSize(25, 25))
        self.fram_up_alarm_point.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_up_alarm_point.setFrameShape(QFrame.WinPanel)
        self._lbl_txt9_3 = QLabel(self.centralwidget)
        self._lbl_txt9_3.setObjectName(u"_lbl_txt9_3")
        self._lbl_txt9_3.setGeometry(QRect(350, 540, 243, 31))
        self._lbl_txt9_3.setFont(font)
        self._lbl_txt9_3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt9_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.lcdH_T = QLCDNumber(self.centralwidget)
        self.lcdH_T.setObjectName(u"lcdH_T")
        self.lcdH_T.setGeometry(QRect(160, 238, 101, 43))
        self.lcdH_T.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.lcdH_T.setSegmentStyle(QLCDNumber.Flat)
        self.lcdH_T.setProperty("value", 0.000000000000000)
        self.lcdH_T.setProperty("intValue", 0)
        self._lbl_txt15_3 = QLabel(self.centralwidget)
        self._lbl_txt15_3.setObjectName(u"_lbl_txt15_3")
        self._lbl_txt15_3.setGeometry(QRect(10, 238, 143, 35))
        self._lbl_txt15_3.setFont(font1)
        self._lbl_txt15_3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt15_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self._lbl_txt5_2 = QLabel(self.centralwidget)
        self._lbl_txt5_2.setObjectName(u"_lbl_txt5_2")
        self._lbl_txt5_2.setGeometry(QRect(350, 222, 243, 23))
        self._lbl_txt5_2.setFont(font)
        self._lbl_txt5_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt5_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_green_light = QLabel(self.centralwidget)
        self.fram_green_light.setObjectName(u"fram_green_light")
        self.fram_green_light.setGeometry(QRect(320, 222, 25, 25))
        self.fram_green_light.setMinimumSize(QSize(20, 20))
        self.fram_green_light.setMaximumSize(QSize(25, 25))
        self.fram_green_light.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_green_light.setFrameShape(QFrame.WinPanel)
        self._lbl_txt6_2 = QLabel(self.centralwidget)
        self._lbl_txt6_2.setObjectName(u"_lbl_txt6_2")
        self._lbl_txt6_2.setGeometry(QRect(350, 185, 243, 23))
        self._lbl_txt6_2.setFont(font)
        self._lbl_txt6_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt6_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.fram_red_light = QLabel(self.centralwidget)
        self.fram_red_light.setObjectName(u"fram_red_light")
        self.fram_red_light.setGeometry(QRect(320, 187, 25, 25))
        self.fram_red_light.setMinimumSize(QSize(20, 20))
        self.fram_red_light.setMaximumSize(QSize(25, 25))
        self.fram_red_light.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_red_light.setFrameShape(QFrame.WinPanel)
        self.btn_green_light = QPushButton(self.centralwidget)
        self.btn_green_light.setObjectName(u"btn_green_light")
        self.btn_green_light.setGeometry(QRect(280, 220, 30, 30))
        self.btn_green_light.setMinimumSize(QSize(30, 30))
        self.btn_green_light.setMaximumSize(QSize(30, 30))
        self.btn_green_light.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_green_light.setCheckable(False)
        self.btn_green_light.setChecked(False)
        self.btn_red_light = QPushButton(self.centralwidget)
        self.btn_red_light.setObjectName(u"btn_red_light")
        self.btn_red_light.setGeometry(QRect(280, 185, 30, 30))
        self.btn_red_light.setMinimumSize(QSize(30, 30))
        self.btn_red_light.setMaximumSize(QSize(30, 30))
        self.btn_red_light.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_red_light.setCheckable(False)
        self.btn_red_light.setChecked(False)
        self._lbl_txt15_4 = QLabel(self.centralwidget)
        self._lbl_txt15_4.setObjectName(u"_lbl_txt15_4")
        self._lbl_txt15_4.setGeometry(QRect(10, 380, 143, 40))
        self._lbl_txt15_4.setFont(font1)
        self._lbl_txt15_4.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt15_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_F_alarm = MyLineEdit(self.centralwidget)
        self.lineEdit_F_alarm.setObjectName(u"lineEdit_F_alarm")
        self.lineEdit_F_alarm.setGeometry(QRect(160, 378, 101, 43))
        font2 = QFont()
        font2.setFamilies([u"Calibri"])
        font2.setPointSize(20)
        font2.setBold(False)
        self.lineEdit_F_alarm.setFont(font2)
        self.lineEdit_F_alarm.setAlignment(Qt.AlignCenter)
        self.fram_yellow_btn = QLabel(self.centralwidget)
        self.fram_yellow_btn.setObjectName(u"fram_yellow_btn")
        self.fram_yellow_btn.setGeometry(QRect(320, 580, 25, 25))
        self.fram_yellow_btn.setMinimumSize(QSize(20, 20))
        self.fram_yellow_btn.setMaximumSize(QSize(25, 25))
        self.fram_yellow_btn.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-color: rgb(0, 0, 0);")
        self.fram_yellow_btn.setFrameShape(QFrame.WinPanel)
        self._lbl_txt6_3 = QLabel(self.centralwidget)
        self._lbl_txt6_3.setObjectName(u"_lbl_txt6_3")
        self._lbl_txt6_3.setGeometry(QRect(350, 580, 243, 23))
        self._lbl_txt6_3.setFont(font)
        self._lbl_txt6_3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt6_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.btn_temper_channel = QPushButton(self.centralwidget)
        self.btn_temper_channel.setObjectName(u"btn_temper_channel")
        self.btn_temper_channel.setGeometry(QRect(280, 115, 30, 30))
        self.btn_temper_channel.setMinimumSize(QSize(30, 30))
        self.btn_temper_channel.setMaximumSize(QSize(30, 30))
        self.btn_temper_channel.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_temper_channel.setCheckable(False)
        self.btn_temper_channel.setChecked(False)
        self.lbl_temp_sens = QLabel(self.centralwidget)
        self.lbl_temp_sens.setObjectName(u"lbl_temp_sens")
        self.lbl_temp_sens.setGeometry(QRect(320, 117, 281, 23))
        self.lbl_temp_sens.setFont(font)
        self.lbl_temp_sens.setLayoutDirection(Qt.LeftToRight)
        self.lbl_temp_sens.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.freq_frame = QFrame(self.centralwidget)
        self.freq_frame.setObjectName(u"freq_frame")
        self.freq_frame.setGeometry(QRect(10, 430, 301, 271))
        self.freq_frame.setFrameShape(QFrame.StyledPanel)
        self.freq_frame.setFrameShadow(QFrame.Raised)
        self._lbl_txt1_3 = QLabel(self.freq_frame)
        self._lbl_txt1_3.setObjectName(u"_lbl_txt1_3")
        self._lbl_txt1_3.setGeometry(QRect(210, 0, 70, 23))
        self._lbl_txt1_3.setFont(font)
        self._lbl_txt1_3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt1_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self._lbl_txt1_2 = QLabel(self.freq_frame)
        self._lbl_txt1_2.setObjectName(u"_lbl_txt1_2")
        self._lbl_txt1_2.setGeometry(QRect(107, 0, 50, 23))
        self._lbl_txt1_2.setFont(font)
        self._lbl_txt1_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt1_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self._lbl_txt19_2 = QLabel(self.freq_frame)
        self._lbl_txt19_2.setObjectName(u"_lbl_txt19_2")
        self._lbl_txt19_2.setGeometry(QRect(13, 60, 90, 31))
        font3 = QFont()
        font3.setFamilies([u"Calibri"])
        font3.setPointSize(10)
        self._lbl_txt19_2.setFont(font3)
        self._lbl_txt19_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt19_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self._lbl_txt19 = QLabel(self.freq_frame)
        self._lbl_txt19.setObjectName(u"_lbl_txt19")
        self._lbl_txt19.setGeometry(QRect(13, 25, 90, 31))
        self._lbl_txt19.setFont(font)
        self._lbl_txt19.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt19.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.btn_hod = QPushButton(self.freq_frame)
        self.btn_hod.setObjectName(u"btn_hod")
        self.btn_hod.setGeometry(QRect(165, 25, 30, 30))
        self.btn_hod.setMinimumSize(QSize(30, 30))
        self.btn_hod.setMaximumSize(QSize(30, 30))
        self.btn_hod.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_hod.setCheckable(False)
        self.btn_hod.setChecked(False)
        self.lineEdit_hod = QLineEdit(self.freq_frame)
        self.lineEdit_hod.setObjectName(u"lineEdit_hod")
        self.lineEdit_hod.setGeometry(QRect(110, 25, 50, 31))
        font4 = QFont()
        font4.setFamilies([u"Calibri"])
        font4.setPointSize(12)
        font4.setBold(False)
        self.lineEdit_hod.setFont(font4)
        self.lineEdit_hod.setAlignment(Qt.AlignCenter)
        self.btn_freq_trverse = QPushButton(self.freq_frame)
        self.btn_freq_trverse.setObjectName(u"btn_freq_trverse")
        self.btn_freq_trverse.setGeometry(QRect(265, 50, 30, 30))
        self.btn_freq_trverse.setMinimumSize(QSize(30, 30))
        self.btn_freq_trverse.setMaximumSize(QSize(30, 30))
        self.btn_freq_trverse.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_freq_trverse.setCheckable(False)
        self.btn_freq_trverse.setChecked(False)
        self.btn_speed_main = QPushButton(self.freq_frame)
        self.btn_speed_main.setObjectName(u"btn_speed_main")
        self.btn_speed_main.setGeometry(QRect(165, 60, 30, 30))
        self.btn_speed_main.setMinimumSize(QSize(30, 30))
        self.btn_speed_main.setMaximumSize(QSize(30, 30))
        self.btn_speed_main.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_speed_main.setCheckable(False)
        self.btn_speed_main.setChecked(False)
        self.lineEdit_freq_traverse = QLineEdit(self.freq_frame)
        self.lineEdit_freq_traverse.setObjectName(u"lineEdit_freq_traverse")
        self.lineEdit_freq_traverse.setGeometry(QRect(210, 50, 50, 31))
        self.lineEdit_freq_traverse.setFont(font4)
        self.lineEdit_freq_traverse.setAlignment(Qt.AlignCenter)
        self.lineEdit_speed_main = QLineEdit(self.freq_frame)
        self.lineEdit_speed_main.setObjectName(u"lineEdit_speed_main")
        self.lineEdit_speed_main.setGeometry(QRect(110, 60, 50, 31))
        self.lineEdit_speed_main.setFont(font4)
        self.lineEdit_speed_main.setAlignment(Qt.AlignCenter)
        self._lbl_txt1_4 = QLabel(self.freq_frame)
        self._lbl_txt1_4.setObjectName(u"_lbl_txt1_4")
        self._lbl_txt1_4.setGeometry(QRect(205, 25, 90, 23))
        self._lbl_txt1_4.setFont(font)
        self._lbl_txt1_4.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt1_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.btn_motor_up = QPushButton(self.freq_frame)
        self.btn_motor_up.setObjectName(u"btn_motor_up")
        self.btn_motor_up.setGeometry(QRect(220, 90, 60, 30))
        self.btn_motor_up.setMinimumSize(QSize(60, 30))
        self.btn_motor_up.setMaximumSize(QSize(60, 50))
        self.btn_motor_up.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"")
        self.btn_motor_up.setCheckable(False)
        self.btn_motor_up.setChecked(False)
        self.btn_motor_down = QPushButton(self.freq_frame)
        self.btn_motor_down.setObjectName(u"btn_motor_down")
        self.btn_motor_down.setGeometry(QRect(220, 130, 60, 30))
        self.btn_motor_down.setMinimumSize(QSize(60, 30))
        self.btn_motor_down.setMaximumSize(QSize(60, 50))
        self.btn_motor_down.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"")
        self.btn_motor_down.setCheckable(False)
        self.btn_motor_down.setChecked(False)
        self.btn_motor_traverse_stop = QPushButton(self.freq_frame)
        self.btn_motor_traverse_stop.setObjectName(u"btn_motor_traverse_stop")
        self.btn_motor_traverse_stop.setGeometry(QRect(220, 170, 60, 60))
        self.btn_motor_traverse_stop.setMinimumSize(QSize(60, 60))
        self.btn_motor_traverse_stop.setMaximumSize(QSize(60, 60))
        self.btn_motor_traverse_stop.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"")
        self.btn_motor_traverse_stop.setCheckable(False)
        self.btn_motor_traverse_stop.setChecked(False)
        self.btn_motor_main_start = QPushButton(self.freq_frame)
        self.btn_motor_main_start.setObjectName(u"btn_motor_main_start")
        self.btn_motor_main_start.setGeometry(QRect(80, 100, 80, 50))
        self.btn_motor_main_start.setMinimumSize(QSize(80, 50))
        self.btn_motor_main_start.setMaximumSize(QSize(80, 50))
        self.btn_motor_main_start.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"")
        self.btn_motor_main_start.setCheckable(False)
        self.btn_motor_main_start.setChecked(False)
        self.btn_motor_main_stop = QPushButton(self.freq_frame)
        self.btn_motor_main_stop.setObjectName(u"btn_motor_main_stop")
        self.btn_motor_main_stop.setGeometry(QRect(80, 160, 80, 50))
        self.btn_motor_main_stop.setMinimumSize(QSize(80, 50))
        self.btn_motor_main_stop.setMaximumSize(QSize(80, 50))
        self.btn_motor_main_stop.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"")
        self.btn_motor_main_stop.setCheckable(False)
        self.btn_motor_main_stop.setChecked(False)
        self.btn_test = QPushButton(self.freq_frame)
        self.btn_test.setObjectName(u"btn_test")
        self.btn_test.setGeometry(QRect(20, 228, 30, 30))
        self.btn_test.setMinimumSize(QSize(30, 30))
        self.btn_test.setMaximumSize(QSize(30, 30))
        self.btn_test.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_test.setCheckable(True)
        self.btn_test.setChecked(False)
        self._lbl_txt10_3 = QLabel(self.freq_frame)
        self._lbl_txt10_3.setObjectName(u"_lbl_txt10_3")
        self._lbl_txt10_3.setGeometry(QRect(60, 230, 121, 23))
        self._lbl_txt10_3.setFont(font)
        self._lbl_txt10_3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt10_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.lcdTemp_2 = QLCDNumber(self.centralwidget)
        self.lcdTemp_2.setObjectName(u"lcdTemp_2")
        self.lcdTemp_2.setGeometry(QRect(160, 330, 101, 43))
        self.lcdTemp_2.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.lcdTemp_2.setSegmentStyle(QLCDNumber.Flat)
        self.lcdTemp_2.setProperty("value", 0.000000000000000)
        self.lcdTemp_2.setProperty("intValue", 0)
        self._lbl_txt15_5 = QLabel(self.centralwidget)
        self._lbl_txt15_5.setObjectName(u"_lbl_txt15_5")
        self._lbl_txt15_5.setGeometry(QRect(10, 332, 143, 31))
        self._lbl_txt15_5.setFont(font1)
        self._lbl_txt15_5.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt15_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.koef_force_lcd = QLCDNumber(self.centralwidget)
        self.koef_force_lcd.setObjectName(u"koef_force_lcd")
        self.koef_force_lcd.setGeometry(QRect(160, 100, 101, 43))
        self.koef_force_lcd.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.koef_force_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.koef_force_lcd.setProperty("value", -100.000000000000000)
        self.koef_force_lcd.setProperty("intValue", -100)
        self._lbl_txt2_2 = QLabel(self.centralwidget)
        self._lbl_txt2_2.setObjectName(u"_lbl_txt2_2")
        self._lbl_txt2_2.setGeometry(QRect(10, 104, 141, 32))
        self._lbl_txt2_2.setFont(font)
        self._lbl_txt2_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt2_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.correct_force_lcd = QLCDNumber(self.centralwidget)
        self.correct_force_lcd.setObjectName(u"correct_force_lcd")
        self.correct_force_lcd.setGeometry(QRect(160, 146, 101, 43))
        self.correct_force_lcd.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.correct_force_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.correct_force_lcd.setProperty("value", -100.000000000000000)
        self.correct_force_lcd.setProperty("intValue", -100)
        self._lbl_txt2_3 = QLabel(self.centralwidget)
        self._lbl_txt2_3.setObjectName(u"_lbl_txt2_3")
        self._lbl_txt2_3.setGeometry(QRect(10, 150, 141, 32))
        self._lbl_txt2_3.setFont(font)
        self._lbl_txt2_3.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt2_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.btn_correct_force = QPushButton(self.centralwidget)
        self.btn_correct_force.setObjectName(u"btn_correct_force")
        self.btn_correct_force.setGeometry(QRect(280, 150, 30, 30))
        self.btn_correct_force.setMinimumSize(QSize(30, 30))
        self.btn_correct_force.setMaximumSize(QSize(30, 30))
        self.btn_correct_force.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 5px;\n"
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
"	background-color: rgb(0, 255, 0)\n"
"	\n"
"}")
        self.btn_correct_force.setCheckable(False)
        self.btn_correct_force.setChecked(False)
        self._lbl_txt3_2 = QLabel(self.centralwidget)
        self._lbl_txt3_2.setObjectName(u"_lbl_txt3_2")
        self._lbl_txt3_2.setGeometry(QRect(320, 152, 243, 23))
        self._lbl_txt3_2.setFont(font)
        self._lbl_txt3_2.setLayoutDirection(Qt.LeftToRight)
        self._lbl_txt3_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        SettingsWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(SettingsWindow)
        self.statusbar.setObjectName(u"statusbar")
        SettingsWindow.setStatusBar(self.statusbar)

        self.retranslateUi(SettingsWindow)

        QMetaObject.connectSlotsByName(SettingsWindow)
    # setupUi

    def retranslateUi(self, SettingsWindow):
        SettingsWindow.setWindowTitle(QCoreApplication.translate("SettingsWindow", u"HandDebug", None))
        self._lbl_txt2.setText(QCoreApplication.translate("SettingsWindow", u"\u0427\u0438\u0441\u0442\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 (\u043a\u0433\u0441):", None))
        self._lbl_txt1.setText(QCoreApplication.translate("SettingsWindow", u"\u0412\u0440\u0435\u043c\u044f (\u043c\u0441):", None))
        self.fram_cycle_F.setText("")
        self.btn_cycle_F.setText("")
        self._lbl_txt3.setText(QCoreApplication.translate("SettingsWindow", u"\u0426\u0438\u043a\u043b\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043e\u043f\u0440\u043e\u0441 \u0434\u0430\u0442\u0447\u0438\u043a\u0430 \u0441\u0438\u043b\u044b", None))
        self._lbl_txt5.setText(QCoreApplication.translate("SettingsWindow", u"\u041f\u043e\u0442\u0435\u0440\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f", None))
        self.fram_no_control.setText("")
        self.btn_no_control.setText("")
        self.btn_max_F.setText("")
        self.fram_max_F.setText("")
        self._lbl_txt6.setText(QCoreApplication.translate("SettingsWindow", u"\u041f\u0440\u0435\u0432\u044b\u0448\u0435\u043d\u0438\u0435 \u0443\u0441\u0438\u043b\u0438\u044f", None))
        self._lbl_txt8.setText(QCoreApplication.translate("SettingsWindow", u"\u041d\u0438\u0436\u043d\u0435\u0435 \u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0442\u0440\u0430\u0432\u0435\u0440\u0441\u044b", None))
        self.fram_down_point.setText("")
        self.fram_up_point.setText("")
        self._lbl_txt9.setText(QCoreApplication.translate("SettingsWindow", u"\u0412\u0435\u0440\u0445\u043d\u0435\u0435 \u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0442\u0440\u0430\u0432\u0435\u0440\u0441\u044b", None))
        self._lbl_txt10.setText(QCoreApplication.translate("SettingsWindow", u"\u0417\u0430\u0449\u0438\u0442\u043d\u043e\u0435 \u043e\u0433\u0440\u0430\u0436\u0434\u0435\u043d\u0438\u0435 \u043e\u0442\u043a\u0440\u044b\u0442\u043e", None))
        self.fram_safety_fence.setText("")
        self.fram_condition_FC.setText("")
        self._lbl_txt11.setText(QCoreApplication.translate("SettingsWindow", u"\u041f\u0427 \u0437\u0430\u043d\u044f\u0442 \u0434\u043b\u044f \u043f\u0440\u0438\u0435\u043c\u0430 \u043a\u043e\u043c\u0430\u043d\u0434", None))
        self._lbl_txt12.setText(QCoreApplication.translate("SettingsWindow", u"\u0414\u0430\u0442\u0447\u0438\u043a \u0443\u0441\u0438\u043b\u0438\u044f \u0437\u0430\u043d\u044f\u0442", None))
        self.fram_sensor_F.setText("")
        self._lbl_txt15.setText(QCoreApplication.translate("SettingsWindow", u"\u041f\u0435\u0440\u0435\u043c\u0435\u0449\u0435\u043d\u0438\u0435\n"
"\u0448\u0430\u0442\u0443\u043d\u0430 (\u043c\u043c):", None))
        self._lbl_txt15_2.setText(QCoreApplication.translate("SettingsWindow", u"\u0411\u0435\u0441\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u044b\u0439\n"
"\u0434\u0430\u0442\u0447\u0438\u043a (\u00b0\u0421):", None))
        self.fram_block_traverse_1.setText("")
        self._lbl_txt8_2.setText(QCoreApplication.translate("SettingsWindow", u"\u0411\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0430 \u0442\u0440\u0430\u0432\u0435\u0440\u0441\u044b 1", None))
        self.fram_block_traverse_2.setText("")
        self._lbl_txt9_2.setText(QCoreApplication.translate("SettingsWindow", u"\u0411\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0430 \u0442\u0440\u0430\u0432\u0435\u0440\u0441\u044b 2", None))
        self.fram_down__alarm_point.setText("")
        self._lbl_txt8_3.setText(QCoreApplication.translate("SettingsWindow", u"\u041d\u0438\u0436\u043d\u0435\u0435 \u0430\u0432\u0430\u0440\u0438\u0439\u043d\u043e\u0435\n"
"\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0442\u0440\u0430\u0432\u0435\u0440\u0441\u044b", None))
        self.fram_up_alarm_point.setText("")
        self._lbl_txt9_3.setText(QCoreApplication.translate("SettingsWindow", u"\u0412\u0435\u0440\u0445\u043d\u0435\u0435 \u0430\u0432\u0430\u0440\u0438\u0439\u043d\u043e\u0435\n"
"\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0442\u0440\u0430\u0432\u0435\u0440\u0441\u044b", None))
        self._lbl_txt15_3.setText(QCoreApplication.translate("SettingsWindow", u"\u041f\u0435\u0440\u0435\u043c\u0435\u0449\u0435\u043d\u0438\u0435\n"
"\u0442\u0440\u0430\u0432\u0435\u0440\u0441\u044b (\u043c\u043c):", None))
        self._lbl_txt5_2.setText(QCoreApplication.translate("SettingsWindow", u"\u0417\u0435\u043b\u0451\u043d\u044b\u0439 \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440", None))
        self.fram_green_light.setText("")
        self._lbl_txt6_2.setText(QCoreApplication.translate("SettingsWindow", u"\u041a\u0440\u0430\u0441\u043d\u044b\u0439 \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440", None))
        self.fram_red_light.setText("")
        self.btn_green_light.setText("")
        self.btn_red_light.setText("")
        self._lbl_txt15_4.setText(QCoreApplication.translate("SettingsWindow", u"\u0410\u0432\u0430\u0440\u0438\u0439\u043d\u043e\u0435\n"
"\u0443\u0441\u0438\u043b\u0438\u0435 (\u043a\u0433\u0441):", None))
        self.lineEdit_F_alarm.setText("")
        self.fram_yellow_btn.setText("")
        self._lbl_txt6_3.setText(QCoreApplication.translate("SettingsWindow", u"\u041a\u043d\u043e\u043f\u043a\u0430 \u041f\u0423\u0421\u041a/\u041e\u0421\u0422\u0410\u041d\u041e\u0412", None))
        self.btn_temper_channel.setText("")
        self.lbl_temp_sens.setText(QCoreApplication.translate("SettingsWindow", u"\u0411\u0435\u0441\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u044b\u0439 \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u043d\u044b\u0439 \u0434\u0430\u0442\u0447\u0438\u043a", None))
        self._lbl_txt1_3.setText(QCoreApplication.translate("SettingsWindow", u"\u0422\u0440\u0430\u0432\u0435\u0440\u0441\u0430", None))
        self._lbl_txt1_2.setText(QCoreApplication.translate("SettingsWindow", u"\u0428\u0430\u0442\u0443\u043d", None))
        self._lbl_txt19_2.setText(QCoreApplication.translate("SettingsWindow", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c, (\u043c/\u0441)", None))
        self._lbl_txt19.setText(QCoreApplication.translate("SettingsWindow", u"\u0425\u043e\u0434, (\u043c\u043c)", None))
        self.btn_hod.setText("")
        self.lineEdit_hod.setText(QCoreApplication.translate("SettingsWindow", u"50", None))
        self.btn_freq_trverse.setText("")
        self.btn_speed_main.setText("")
        self.lineEdit_freq_traverse.setText("")
        self.lineEdit_speed_main.setText("")
        self._lbl_txt1_4.setText(QCoreApplication.translate("SettingsWindow", u"\u0427\u0430\u0441\u0442\u043e\u0442\u0430, (\u0413\u0446)", None))
        self.btn_motor_up.setText(QCoreApplication.translate("SettingsWindow", u"\u0412\u0412\u0415\u0420\u0425", None))
        self.btn_motor_down.setText(QCoreApplication.translate("SettingsWindow", u"\u0412\u041d\u0418\u0417", None))
        self.btn_motor_traverse_stop.setText(QCoreApplication.translate("SettingsWindow", u"\u0421\u0422\u041e\u041f", None))
        self.btn_motor_main_start.setText(QCoreApplication.translate("SettingsWindow", u"\u0421\u0422\u0410\u0420\u0422\n"
"\u041f\u0420\u0418\u0412\u041e\u0414", None))
        self.btn_motor_main_stop.setText(QCoreApplication.translate("SettingsWindow", u"\u0421\u0422\u041e\u041f\n"
"\u041f\u0420\u0418\u0412\u041e\u0414", None))
        self.btn_test.setText("")
        self._lbl_txt10_3.setText(QCoreApplication.translate("SettingsWindow", u"\u0427\u0442\u0435\u043d\u0438\u0435 \u0431\u0443\u0444\u0435\u0440\u0430", None))
        self._lbl_txt15_5.setText(QCoreApplication.translate("SettingsWindow", u"\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u044b\u0439\n"
"\u0434\u0430\u0442\u0447\u0438\u043a (\u00b0\u0421):", None))
        self._lbl_txt2_2.setText(QCoreApplication.translate("SettingsWindow", u"\u0421\u043a\u043e\u0440\u0440\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0435\n"
"\u0443\u0441\u0438\u043b\u0438\u0435 (\u043a\u0433\u0441):", None))
        self._lbl_txt2_3.setText(QCoreApplication.translate("SettingsWindow", u"\u041e\u0431\u043d\u0443\u043b\u0451\u043d\u043d\u043e\u0435\n"
"\u0443\u0441\u0438\u043b\u0438\u0435 (\u043a\u0433\u0441):", None))
        self.btn_correct_force.setText("")
        self._lbl_txt3_2.setText(QCoreApplication.translate("SettingsWindow", u"\u041e\u0431\u043d\u0443\u043b\u0438\u0442\u044c \u0434\u0430\u0442\u0447\u0438\u043a \u0441\u0438\u043b\u044b", None))
    # retranslateUi

