# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'archive_uiUqaCdH.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QStackedWidget,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from pyqtgraph import PlotWidget

class Ui_WindowArch(object):
    def setupUi(self, WindowArch):
        if not WindowArch.objectName():
            WindowArch.setObjectName(u"WindowArch")
        WindowArch.resize(1024, 940)
        WindowArch.setMinimumSize(QSize(1024, 940))
        WindowArch.setMaximumSize(QSize(1024, 940))
        WindowArch.setStyleSheet(u"")
        self.centralwidget = QWidget(WindowArch)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(1024, 920))
        self.centralwidget.setMaximumSize(QSize(1024, 920))
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_title = QFrame(self.centralwidget)
        self.frame_title.setObjectName(u"frame_title")
        self.frame_title.setMinimumSize(QSize(0, 40))
        self.frame_title.setMaximumSize(QSize(16777215, 40))
        self.frame_title.setFrameShape(QFrame.StyledPanel)
        self.frame_title.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_title)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.combo_dates = QComboBox(self.frame_title)
        self.combo_dates.setObjectName(u"combo_dates")
        self.combo_dates.setMinimumSize(QSize(130, 30))
        self.combo_dates.setMaximumSize(QSize(130, 30))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(14)
        self.combo_dates.setFont(font)

        self.horizontalLayout.addWidget(self.combo_dates)

        self.combo_type_test = QComboBox(self.frame_title)
        self.combo_type_test.addItem("")
        self.combo_type_test.addItem("")
        self.combo_type_test.addItem("")
        self.combo_type_test.addItem("")
        self.combo_type_test.setObjectName(u"combo_type_test")
        self.combo_type_test.setMinimumSize(QSize(130, 30))
        self.combo_type_test.setMaximumSize(QSize(150, 30))
        self.combo_type_test.setFont(font)

        self.horizontalLayout.addWidget(self.combo_type_test)

        self.combo_test = QComboBox(self.frame_title)
        self.combo_test.setObjectName(u"combo_test")
        self.combo_test.setMinimumSize(QSize(400, 30))
        self.combo_test.setMaximumSize(QSize(400, 30))
        self.combo_test.setFont(font)

        self.horizontalLayout.addWidget(self.combo_test)

        self.combo_type = QComboBox(self.frame_title)
        self.combo_type.setObjectName(u"combo_type")
        self.combo_type.setMinimumSize(QSize(290, 30))
        self.combo_type.setMaximumSize(QSize(290, 30))
        self.combo_type.setFont(font)

        self.horizontalLayout.addWidget(self.combo_type)


        self.verticalLayout.addWidget(self.frame_title)

        self.frame_content = QFrame(self.centralwidget)
        self.frame_content.setObjectName(u"frame_content")
        self.frame_content.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.frame_content.setFrameShape(QFrame.StyledPanel)
        self.frame_content.setFrameShadow(QFrame.Raised)
        self.stackedWidget = QStackedWidget(self.frame_content)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(10, 10, 1000, 590))
        self.duble_graph_page = QWidget()
        self.duble_graph_page.setObjectName(u"duble_graph_page")
        self.duble_graphwidget = PlotWidget(self.duble_graph_page)
        self.duble_graphwidget.setObjectName(u"duble_graphwidget")
        self.duble_graphwidget.setGeometry(QRect(0, 0, 1000, 590))
        self.duble_graphwidget.setMinimumSize(QSize(0, 530))
        self.duble_graphwidget.setMaximumSize(QSize(16777215, 16777215))
        self.duble_graphwidget.setAutoFillBackground(False)
        self.duble_graphwidget.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.stackedWidget.addWidget(self.duble_graph_page)
        self.triple_graph_page = QWidget()
        self.triple_graph_page.setObjectName(u"triple_graph_page")
        self.triple_graphwidget = PlotWidget(self.triple_graph_page)
        self.triple_graphwidget.setObjectName(u"triple_graphwidget")
        self.triple_graphwidget.setGeometry(QRect(0, 0, 1000, 590))
        self.triple_graphwidget.setMinimumSize(QSize(0, 530))
        self.triple_graphwidget.setMaximumSize(QSize(16777215, 16777215))
        self.triple_graphwidget.setAutoFillBackground(False)
        self.triple_graphwidget.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.stackedWidget.addWidget(self.triple_graph_page)
        self.basic_frame = QFrame(self.frame_content)
        self.basic_frame.setObjectName(u"basic_frame")
        self.basic_frame.setGeometry(QRect(10, 600, 1000, 65))
        self.basic_frame.setFrameShape(QFrame.StyledPanel)
        self.basic_frame.setFrameShadow(QFrame.Raised)
        self.lbl_14 = QLabel(self.basic_frame)
        self.lbl_14.setObjectName(u"lbl_14")
        self.lbl_14.setGeometry(QRect(10, 5, 121, 25))
        self.lbl_14.setMinimumSize(QSize(0, 25))
        self.lbl_14.setMaximumSize(QSize(16777215, 25))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(12)
        self.lbl_14.setFont(font1)
        self.lbl_16 = QLabel(self.basic_frame)
        self.lbl_16.setObjectName(u"lbl_16")
        self.lbl_16.setGeometry(QRect(10, 35, 121, 25))
        self.lbl_16.setMinimumSize(QSize(0, 25))
        self.lbl_16.setMaximumSize(QSize(16777215, 25))
        self.lbl_16.setFont(font1)
        self.name_le = QLineEdit(self.basic_frame)
        self.name_le.setObjectName(u"name_le")
        self.name_le.setGeometry(QRect(270, 5, 350, 25))
        self.name_le.setMinimumSize(QSize(350, 25))
        self.name_le.setMaximumSize(QSize(350, 25))
        self.name_le.setFont(font)
        self.name_le.setAlignment(Qt.AlignCenter)
        self.name_le.setReadOnly(True)
        self.operator_le = QLineEdit(self.basic_frame)
        self.operator_le.setObjectName(u"operator_le")
        self.operator_le.setGeometry(QRect(270, 35, 350, 25))
        self.operator_le.setMinimumSize(QSize(350, 25))
        self.operator_le.setMaximumSize(QSize(350, 25))
        self.operator_le.setFont(font)
        self.operator_le.setAlignment(Qt.AlignCenter)
        self.operator_le.setReadOnly(True)
        self.lbl_23 = QLabel(self.basic_frame)
        self.lbl_23.setObjectName(u"lbl_23")
        self.lbl_23.setGeometry(QRect(640, 5, 128, 25))
        self.lbl_23.setMinimumSize(QSize(0, 25))
        self.lbl_23.setMaximumSize(QSize(16777215, 25))
        self.lbl_23.setFont(font1)
        self.lbl_27 = QLabel(self.basic_frame)
        self.lbl_27.setObjectName(u"lbl_27")
        self.lbl_27.setGeometry(QRect(640, 35, 128, 25))
        self.lbl_27.setMinimumSize(QSize(0, 25))
        self.lbl_27.setMaximumSize(QSize(16777215, 25))
        self.lbl_27.setFont(font1)
        self.serial_le = QLineEdit(self.basic_frame)
        self.serial_le.setObjectName(u"serial_le")
        self.serial_le.setGeometry(QRect(780, 5, 210, 25))
        self.serial_le.setMinimumSize(QSize(210, 25))
        self.serial_le.setMaximumSize(QSize(210, 25))
        self.serial_le.setFont(font)
        self.serial_le.setAlignment(Qt.AlignCenter)
        self.serial_le.setReadOnly(True)
        self.date_le = QLineEdit(self.basic_frame)
        self.date_le.setObjectName(u"date_le")
        self.date_le.setGeometry(QRect(780, 35, 210, 25))
        self.date_le.setMinimumSize(QSize(210, 25))
        self.date_le.setMaximumSize(QSize(210, 25))
        self.date_le.setFont(font)
        self.date_le.setAlignment(Qt.AlignCenter)
        self.date_le.setReadOnly(True)
        self.data_stWd = QStackedWidget(self.frame_content)
        self.data_stWd.setObjectName(u"data_stWd")
        self.data_stWd.setGeometry(QRect(10, 665, 1000, 160))
        self.base_page = QWidget()
        self.base_page.setObjectName(u"base_page")
        self.lbl_21 = QLabel(self.base_page)
        self.lbl_21.setObjectName(u"lbl_21")
        self.lbl_21.setGeometry(QRect(10, 5, 250, 25))
        self.lbl_21.setMinimumSize(QSize(0, 25))
        self.lbl_21.setMaximumSize(QSize(16777215, 25))
        self.lbl_21.setFont(font1)
        self.lbl_26 = QLabel(self.base_page)
        self.lbl_26.setObjectName(u"lbl_26")
        self.lbl_26.setGeometry(QRect(10, 35, 250, 25))
        self.lbl_26.setMinimumSize(QSize(0, 25))
        self.lbl_26.setMaximumSize(QSize(16777215, 25))
        self.lbl_26.setFont(font1)
        self.lbl_25 = QLabel(self.base_page)
        self.lbl_25.setObjectName(u"lbl_25")
        self.lbl_25.setGeometry(QRect(10, 65, 211, 25))
        self.lbl_25.setMinimumSize(QSize(0, 25))
        self.lbl_25.setMaximumSize(QSize(16777215, 25))
        self.lbl_25.setFont(font1)
        self.lbl_20 = QLabel(self.base_page)
        self.lbl_20.setObjectName(u"lbl_20")
        self.lbl_20.setGeometry(QRect(10, 95, 208, 25))
        self.lbl_20.setMinimumSize(QSize(0, 25))
        self.lbl_20.setMaximumSize(QSize(16777215, 25))
        self.lbl_20.setFont(font1)
        self.lbl_17 = QLabel(self.base_page)
        self.lbl_17.setObjectName(u"lbl_17")
        self.lbl_17.setGeometry(QRect(10, 125, 216, 25))
        self.lbl_17.setMinimumSize(QSize(0, 25))
        self.lbl_17.setMaximumSize(QSize(16777215, 25))
        self.lbl_17.setFont(font1)
        self.recoil_base_le = QLineEdit(self.base_page)
        self.recoil_base_le.setObjectName(u"recoil_base_le")
        self.recoil_base_le.setGeometry(QRect(270, 5, 100, 25))
        self.recoil_base_le.setMinimumSize(QSize(100, 25))
        self.recoil_base_le.setMaximumSize(QSize(100, 25))
        self.recoil_base_le.setFont(font)
        self.recoil_base_le.setAlignment(Qt.AlignCenter)
        self.recoil_base_le.setReadOnly(True)
        self.comp_base_le = QLineEdit(self.base_page)
        self.comp_base_le.setObjectName(u"comp_base_le")
        self.comp_base_le.setGeometry(QRect(270, 35, 100, 25))
        self.comp_base_le.setMinimumSize(QSize(100, 25))
        self.comp_base_le.setMaximumSize(QSize(100, 25))
        self.comp_base_le.setFont(font)
        self.comp_base_le.setAlignment(Qt.AlignCenter)
        self.comp_base_le.setReadOnly(True)
        self.speed_set_1_base_le = QLineEdit(self.base_page)
        self.speed_set_1_base_le.setObjectName(u"speed_set_1_base_le")
        self.speed_set_1_base_le.setGeometry(QRect(270, 65, 80, 25))
        self.speed_set_1_base_le.setMinimumSize(QSize(80, 25))
        self.speed_set_1_base_le.setMaximumSize(QSize(80, 25))
        self.speed_set_1_base_le.setFont(font)
        self.speed_set_1_base_le.setAlignment(Qt.AlignCenter)
        self.speed_set_1_base_le.setReadOnly(True)
        self.limit_recoil_1_base_le = QLineEdit(self.base_page)
        self.limit_recoil_1_base_le.setObjectName(u"limit_recoil_1_base_le")
        self.limit_recoil_1_base_le.setGeometry(QRect(270, 95, 120, 25))
        self.limit_recoil_1_base_le.setMinimumSize(QSize(120, 25))
        self.limit_recoil_1_base_le.setMaximumSize(QSize(120, 25))
        self.limit_recoil_1_base_le.setFont(font)
        self.limit_recoil_1_base_le.setAlignment(Qt.AlignCenter)
        self.limit_recoil_1_base_le.setReadOnly(True)
        self.limit_comp_1_base_le = QLineEdit(self.base_page)
        self.limit_comp_1_base_le.setObjectName(u"limit_comp_1_base_le")
        self.limit_comp_1_base_le.setGeometry(QRect(270, 125, 120, 25))
        self.limit_comp_1_base_le.setMinimumSize(QSize(120, 25))
        self.limit_comp_1_base_le.setMaximumSize(QSize(120, 25))
        self.limit_comp_1_base_le.setFont(font)
        self.limit_comp_1_base_le.setAlignment(Qt.AlignCenter)
        self.limit_comp_1_base_le.setReadOnly(True)
        self.power_lbl = QLabel(self.base_page)
        self.power_lbl.setObjectName(u"power_lbl")
        self.power_lbl.setGeometry(QRect(400, 5, 110, 25))
        self.power_lbl.setMinimumSize(QSize(0, 25))
        self.power_lbl.setMaximumSize(QSize(16777215, 25))
        self.power_lbl.setFont(font1)
        self.power_lbl_2 = QLabel(self.base_page)
        self.power_lbl_2.setObjectName(u"power_lbl_2")
        self.power_lbl_2.setGeometry(QRect(400, 35, 110, 25))
        self.power_lbl_2.setMinimumSize(QSize(0, 25))
        self.power_lbl_2.setMaximumSize(QSize(16777215, 25))
        self.power_lbl_2.setFont(font1)
        self.speed_set_2_base_le = QLineEdit(self.base_page)
        self.speed_set_2_base_le.setObjectName(u"speed_set_2_base_le")
        self.speed_set_2_base_le.setGeometry(QRect(400, 65, 80, 25))
        self.speed_set_2_base_le.setMinimumSize(QSize(80, 25))
        self.speed_set_2_base_le.setMaximumSize(QSize(80, 25))
        self.speed_set_2_base_le.setFont(font)
        self.speed_set_2_base_le.setAlignment(Qt.AlignCenter)
        self.speed_set_2_base_le.setReadOnly(True)
        self.limit_recoil_2_base_le = QLineEdit(self.base_page)
        self.limit_recoil_2_base_le.setObjectName(u"limit_recoil_2_base_le")
        self.limit_recoil_2_base_le.setGeometry(QRect(400, 95, 120, 25))
        self.limit_recoil_2_base_le.setMinimumSize(QSize(120, 25))
        self.limit_recoil_2_base_le.setMaximumSize(QSize(120, 25))
        self.limit_recoil_2_base_le.setFont(font)
        self.limit_recoil_2_base_le.setAlignment(Qt.AlignCenter)
        self.limit_recoil_2_base_le.setReadOnly(True)
        self.limit_comp_2_base_le = QLineEdit(self.base_page)
        self.limit_comp_2_base_le.setObjectName(u"limit_comp_2_base_le")
        self.limit_comp_2_base_le.setGeometry(QRect(400, 125, 120, 25))
        self.limit_comp_2_base_le.setMinimumSize(QSize(120, 25))
        self.limit_comp_2_base_le.setMaximumSize(QSize(120, 25))
        self.limit_comp_2_base_le.setFont(font)
        self.limit_comp_2_base_le.setAlignment(Qt.AlignCenter)
        self.limit_comp_2_base_le.setReadOnly(True)
        self.power_base_le = QLineEdit(self.base_page)
        self.power_base_le.setObjectName(u"power_base_le")
        self.power_base_le.setGeometry(QRect(540, 5, 80, 25))
        self.power_base_le.setMinimumSize(QSize(80, 25))
        self.power_base_le.setMaximumSize(QSize(80, 25))
        self.power_base_le.setFont(font)
        self.power_base_le.setAlignment(Qt.AlignCenter)
        self.power_base_le.setReadOnly(True)
        self.freq_base_le = QLineEdit(self.base_page)
        self.freq_base_le.setObjectName(u"freq_base_le")
        self.freq_base_le.setGeometry(QRect(540, 35, 80, 25))
        self.freq_base_le.setMinimumSize(QSize(80, 25))
        self.freq_base_le.setMaximumSize(QSize(80, 25))
        self.freq_base_le.setFont(font)
        self.freq_base_le.setAlignment(Qt.AlignCenter)
        self.freq_base_le.setReadOnly(True)
        self.lbl_22 = QLabel(self.base_page)
        self.lbl_22.setObjectName(u"lbl_22")
        self.lbl_22.setGeometry(QRect(640, 5, 211, 25))
        self.lbl_22.setMinimumSize(QSize(0, 25))
        self.lbl_22.setMaximumSize(QSize(16777215, 25))
        self.lbl_22.setFont(font1)
        self.lbl_24 = QLabel(self.base_page)
        self.lbl_24.setObjectName(u"lbl_24")
        self.lbl_24.setGeometry(QRect(640, 35, 186, 25))
        self.lbl_24.setMinimumSize(QSize(0, 25))
        self.lbl_24.setMaximumSize(QSize(16777215, 25))
        self.lbl_24.setFont(font1)
        self.lbl_15 = QLabel(self.base_page)
        self.lbl_15.setObjectName(u"lbl_15")
        self.lbl_15.setGeometry(QRect(640, 65, 235, 25))
        self.lbl_15.setMinimumSize(QSize(0, 25))
        self.lbl_15.setMaximumSize(QSize(16777215, 25))
        self.lbl_15.setFont(font1)
        self.lbl_base_push_force = QLabel(self.base_page)
        self.lbl_base_push_force.setObjectName(u"lbl_base_push_force")
        self.lbl_base_push_force.setGeometry(QRect(525, 95, 350, 25))
        self.lbl_base_push_force.setMinimumSize(QSize(0, 25))
        self.lbl_base_push_force.setMaximumSize(QSize(16777215, 25))
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(12)
        font2.setBold(False)
        self.lbl_base_push_force.setFont(font2)
        self.lbl_base_push_force.setTextFormat(Qt.AutoText)
        self.lbl_base_push_force.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.speed_base_le = QLineEdit(self.base_page)
        self.speed_base_le.setObjectName(u"speed_base_le")
        self.speed_base_le.setGeometry(QRect(900, 5, 80, 25))
        self.speed_base_le.setMinimumSize(QSize(80, 25))
        self.speed_base_le.setMaximumSize(QSize(80, 25))
        self.speed_base_le.setFont(font)
        self.speed_base_le.setAlignment(Qt.AlignCenter)
        self.speed_base_le.setReadOnly(True)
        self.hod_base_le = QLineEdit(self.base_page)
        self.hod_base_le.setObjectName(u"hod_base_le")
        self.hod_base_le.setGeometry(QRect(900, 35, 80, 25))
        self.hod_base_le.setMinimumSize(QSize(80, 25))
        self.hod_base_le.setMaximumSize(QSize(80, 25))
        self.hod_base_le.setFont(font)
        self.hod_base_le.setAlignment(Qt.AlignCenter)
        self.hod_base_le.setReadOnly(True)
        self.max_temp_base_le = QLineEdit(self.base_page)
        self.max_temp_base_le.setObjectName(u"max_temp_base_le")
        self.max_temp_base_le.setGeometry(QRect(900, 65, 80, 25))
        self.max_temp_base_le.setMinimumSize(QSize(80, 25))
        self.max_temp_base_le.setMaximumSize(QSize(80, 25))
        self.max_temp_base_le.setFont(font)
        self.max_temp_base_le.setAlignment(Qt.AlignCenter)
        self.max_temp_base_le.setReadOnly(True)
        self.push_force_base_le = QLineEdit(self.base_page)
        self.push_force_base_le.setObjectName(u"push_force_base_le")
        self.push_force_base_le.setGeometry(QRect(900, 95, 80, 25))
        self.push_force_base_le.setMinimumSize(QSize(80, 25))
        self.push_force_base_le.setMaximumSize(QSize(80, 25))
        self.push_force_base_le.setFont(font)
        self.push_force_base_le.setAlignment(Qt.AlignCenter)
        self.push_force_base_le.setReadOnly(True)
        self.data_stWd.addWidget(self.base_page)
        self.temp_page = QWidget()
        self.temp_page.setObjectName(u"temp_page")
        self.lbl_28 = QLabel(self.temp_page)
        self.lbl_28.setObjectName(u"lbl_28")
        self.lbl_28.setGeometry(QRect(600, 5, 211, 25))
        self.lbl_28.setMinimumSize(QSize(0, 25))
        self.lbl_28.setMaximumSize(QSize(16777215, 25))
        self.lbl_28.setFont(font1)
        self.lbl_29 = QLabel(self.temp_page)
        self.lbl_29.setObjectName(u"lbl_29")
        self.lbl_29.setGeometry(QRect(600, 35, 186, 25))
        self.lbl_29.setMinimumSize(QSize(0, 25))
        self.lbl_29.setMaximumSize(QSize(16777215, 25))
        self.lbl_29.setFont(font1)
        self.lbl_18 = QLabel(self.temp_page)
        self.lbl_18.setObjectName(u"lbl_18")
        self.lbl_18.setGeometry(QRect(600, 95, 235, 25))
        self.lbl_18.setMinimumSize(QSize(0, 25))
        self.lbl_18.setMaximumSize(QSize(16777215, 25))
        self.lbl_18.setFont(font1)
        self.lbl_temp_push_force = QLabel(self.temp_page)
        self.lbl_temp_push_force.setObjectName(u"lbl_temp_push_force")
        self.lbl_temp_push_force.setGeometry(QRect(485, 125, 350, 25))
        self.lbl_temp_push_force.setMinimumSize(QSize(0, 25))
        self.lbl_temp_push_force.setMaximumSize(QSize(16777215, 25))
        self.lbl_temp_push_force.setFont(font2)
        self.lbl_temp_push_force.setTextFormat(Qt.AutoText)
        self.lbl_temp_push_force.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.speed_temp_le = QLineEdit(self.temp_page)
        self.speed_temp_le.setObjectName(u"speed_temp_le")
        self.speed_temp_le.setGeometry(QRect(860, 5, 80, 25))
        self.speed_temp_le.setMinimumSize(QSize(80, 25))
        self.speed_temp_le.setMaximumSize(QSize(80, 25))
        self.speed_temp_le.setFont(font)
        self.speed_temp_le.setAlignment(Qt.AlignCenter)
        self.speed_temp_le.setReadOnly(True)
        self.hod_temp_le = QLineEdit(self.temp_page)
        self.hod_temp_le.setObjectName(u"hod_temp_le")
        self.hod_temp_le.setGeometry(QRect(860, 35, 80, 25))
        self.hod_temp_le.setMinimumSize(QSize(80, 25))
        self.hod_temp_le.setMaximumSize(QSize(80, 25))
        self.hod_temp_le.setFont(font)
        self.hod_temp_le.setAlignment(Qt.AlignCenter)
        self.hod_temp_le.setReadOnly(True)
        self.max_temp_le = QLineEdit(self.temp_page)
        self.max_temp_le.setObjectName(u"max_temp_le")
        self.max_temp_le.setGeometry(QRect(860, 95, 80, 25))
        self.max_temp_le.setMinimumSize(QSize(80, 25))
        self.max_temp_le.setMaximumSize(QSize(80, 25))
        self.max_temp_le.setFont(font)
        self.max_temp_le.setAlignment(Qt.AlignCenter)
        self.max_temp_le.setReadOnly(True)
        self.push_force_temp_le = QLineEdit(self.temp_page)
        self.push_force_temp_le.setObjectName(u"push_force_temp_le")
        self.push_force_temp_le.setGeometry(QRect(860, 125, 80, 25))
        self.push_force_temp_le.setMinimumSize(QSize(80, 25))
        self.push_force_temp_le.setMaximumSize(QSize(80, 25))
        self.push_force_temp_le.setFont(font)
        self.push_force_temp_le.setAlignment(Qt.AlignCenter)
        self.push_force_temp_le.setReadOnly(True)
        self.lbl_19 = QLabel(self.temp_page)
        self.lbl_19.setObjectName(u"lbl_19")
        self.lbl_19.setGeometry(QRect(600, 65, 235, 25))
        self.lbl_19.setMinimumSize(QSize(0, 25))
        self.lbl_19.setMaximumSize(QSize(16777215, 25))
        self.lbl_19.setFont(font1)
        self.begin_temp_le = QLineEdit(self.temp_page)
        self.begin_temp_le.setObjectName(u"begin_temp_le")
        self.begin_temp_le.setGeometry(QRect(860, 65, 80, 25))
        self.begin_temp_le.setMinimumSize(QSize(80, 25))
        self.begin_temp_le.setMaximumSize(QSize(80, 25))
        self.begin_temp_le.setFont(font)
        self.begin_temp_le.setAlignment(Qt.AlignCenter)
        self.begin_temp_le.setReadOnly(True)
        self.lbl_30 = QLabel(self.temp_page)
        self.lbl_30.setObjectName(u"lbl_30")
        self.lbl_30.setGeometry(QRect(50, 40, 250, 25))
        self.lbl_30.setMinimumSize(QSize(0, 25))
        self.lbl_30.setMaximumSize(QSize(16777215, 25))
        self.lbl_30.setFont(font1)
        self.lbl_31 = QLabel(self.temp_page)
        self.lbl_31.setObjectName(u"lbl_31")
        self.lbl_31.setGeometry(QRect(50, 100, 250, 25))
        self.lbl_31.setMinimumSize(QSize(0, 25))
        self.lbl_31.setMaximumSize(QSize(16777215, 25))
        self.lbl_31.setFont(font1)
        self.recoil_end_temp_le = QLineEdit(self.temp_page)
        self.recoil_end_temp_le.setObjectName(u"recoil_end_temp_le")
        self.recoil_end_temp_le.setGeometry(QRect(310, 40, 100, 25))
        self.recoil_end_temp_le.setMinimumSize(QSize(100, 25))
        self.recoil_end_temp_le.setMaximumSize(QSize(100, 25))
        self.recoil_end_temp_le.setFont(font)
        self.recoil_end_temp_le.setAlignment(Qt.AlignCenter)
        self.recoil_end_temp_le.setReadOnly(True)
        self.comp_end_temp_le = QLineEdit(self.temp_page)
        self.comp_end_temp_le.setObjectName(u"comp_end_temp_le")
        self.comp_end_temp_le.setGeometry(QRect(310, 100, 100, 25))
        self.comp_end_temp_le.setMinimumSize(QSize(100, 25))
        self.comp_end_temp_le.setMaximumSize(QSize(100, 25))
        self.comp_end_temp_le.setFont(font)
        self.comp_end_temp_le.setAlignment(Qt.AlignCenter)
        self.comp_end_temp_le.setReadOnly(True)
        self.lbl_32 = QLabel(self.temp_page)
        self.lbl_32.setObjectName(u"lbl_32")
        self.lbl_32.setGeometry(QRect(50, 10, 250, 25))
        self.lbl_32.setMinimumSize(QSize(0, 25))
        self.lbl_32.setMaximumSize(QSize(16777215, 25))
        self.lbl_32.setFont(font1)
        self.lbl_33 = QLabel(self.temp_page)
        self.lbl_33.setObjectName(u"lbl_33")
        self.lbl_33.setGeometry(QRect(50, 70, 250, 25))
        self.lbl_33.setMinimumSize(QSize(0, 25))
        self.lbl_33.setMaximumSize(QSize(16777215, 25))
        self.lbl_33.setFont(font1)
        self.recoil_begin_temp_le = QLineEdit(self.temp_page)
        self.recoil_begin_temp_le.setObjectName(u"recoil_begin_temp_le")
        self.recoil_begin_temp_le.setGeometry(QRect(310, 10, 100, 25))
        self.recoil_begin_temp_le.setMinimumSize(QSize(100, 25))
        self.recoil_begin_temp_le.setMaximumSize(QSize(100, 25))
        self.recoil_begin_temp_le.setFont(font)
        self.recoil_begin_temp_le.setAlignment(Qt.AlignCenter)
        self.recoil_begin_temp_le.setReadOnly(True)
        self.comp_begin_temp_le = QLineEdit(self.temp_page)
        self.comp_begin_temp_le.setObjectName(u"comp_begin_temp_le")
        self.comp_begin_temp_le.setGeometry(QRect(310, 70, 100, 25))
        self.comp_begin_temp_le.setMinimumSize(QSize(100, 25))
        self.comp_begin_temp_le.setMaximumSize(QSize(100, 25))
        self.comp_begin_temp_le.setFont(font)
        self.comp_begin_temp_le.setAlignment(Qt.AlignCenter)
        self.comp_begin_temp_le.setReadOnly(True)
        self.data_stWd.addWidget(self.temp_page)
        self.casc_page = QWidget()
        self.casc_page.setObjectName(u"casc_page")
        self.lbl_35 = QLabel(self.casc_page)
        self.lbl_35.setObjectName(u"lbl_35")
        self.lbl_35.setGeometry(QRect(10, 10, 121, 25))
        self.lbl_35.setMinimumSize(QSize(0, 25))
        self.lbl_35.setMaximumSize(QSize(16777215, 25))
        self.lbl_35.setFont(font1)
        self.hod_casc_le = QLineEdit(self.casc_page)
        self.hod_casc_le.setObjectName(u"hod_casc_le")
        self.hod_casc_le.setGeometry(QRect(140, 10, 80, 25))
        self.hod_casc_le.setMinimumSize(QSize(80, 25))
        self.hod_casc_le.setMaximumSize(QSize(80, 25))
        self.hod_casc_le.setFont(font)
        self.hod_casc_le.setAlignment(Qt.AlignCenter)
        self.hod_casc_le.setReadOnly(True)
        self.lbl_36 = QLabel(self.casc_page)
        self.lbl_36.setObjectName(u"lbl_36")
        self.lbl_36.setGeometry(QRect(670, 10, 235, 25))
        self.lbl_36.setMinimumSize(QSize(0, 25))
        self.lbl_36.setMaximumSize(QSize(16777215, 25))
        self.lbl_36.setFont(font1)
        self.lbl_casc_push_force = QLabel(self.casc_page)
        self.lbl_casc_push_force.setObjectName(u"lbl_casc_push_force")
        self.lbl_casc_push_force.setGeometry(QRect(225, 10, 350, 25))
        self.lbl_casc_push_force.setMinimumSize(QSize(0, 25))
        self.lbl_casc_push_force.setMaximumSize(QSize(16777215, 25))
        self.lbl_casc_push_force.setFont(font2)
        self.lbl_casc_push_force.setTextFormat(Qt.AutoText)
        self.lbl_casc_push_force.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.max_temp_casc_le = QLineEdit(self.casc_page)
        self.max_temp_casc_le.setObjectName(u"max_temp_casc_le")
        self.max_temp_casc_le.setGeometry(QRect(910, 10, 80, 25))
        self.max_temp_casc_le.setMinimumSize(QSize(80, 25))
        self.max_temp_casc_le.setMaximumSize(QSize(80, 25))
        self.max_temp_casc_le.setFont(font)
        self.max_temp_casc_le.setAlignment(Qt.AlignCenter)
        self.max_temp_casc_le.setReadOnly(True)
        self.push_force_casc_le = QLineEdit(self.casc_page)
        self.push_force_casc_le.setObjectName(u"push_force_casc_le")
        self.push_force_casc_le.setGeometry(QRect(580, 10, 80, 25))
        self.push_force_casc_le.setMinimumSize(QSize(80, 25))
        self.push_force_casc_le.setMaximumSize(QSize(80, 25))
        self.push_force_casc_le.setFont(font)
        self.push_force_casc_le.setAlignment(Qt.AlignCenter)
        self.push_force_casc_le.setReadOnly(True)
        self.casc_tableWt = QTableWidget(self.casc_page)
        if (self.casc_tableWt.columnCount() < 30):
            self.casc_tableWt.setColumnCount(30)
        __qtablewidgetitem = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(9, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(10, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.casc_tableWt.setHorizontalHeaderItem(11, __qtablewidgetitem11)
        if (self.casc_tableWt.rowCount() < 3):
            self.casc_tableWt.setRowCount(3)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.casc_tableWt.setVerticalHeaderItem(0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.casc_tableWt.setVerticalHeaderItem(1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.casc_tableWt.setVerticalHeaderItem(2, __qtablewidgetitem14)
        self.casc_tableWt.setObjectName(u"casc_tableWt")
        self.casc_tableWt.setGeometry(QRect(10, 45, 980, 110))
        self.casc_tableWt.setColumnCount(30)
        self.casc_tableWt.horizontalHeader().setVisible(False)
        self.casc_tableWt.horizontalHeader().setDefaultSectionSize(74)
        self.data_stWd.addWidget(self.casc_page)

        self.verticalLayout.addWidget(self.frame_content)

        self.frame_btn = QFrame(self.centralwidget)
        self.frame_btn.setObjectName(u"frame_btn")
        self.frame_btn.setMinimumSize(QSize(0, 50))
        self.frame_btn.setMaximumSize(QSize(16777215, 50))
        self.frame_btn.setFrameShape(QFrame.StyledPanel)
        self.frame_btn.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_btn)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.btn_compare = QPushButton(self.frame_btn)
        self.btn_compare.setObjectName(u"btn_compare")
        self.btn_compare.setMinimumSize(QSize(130, 35))
        self.btn_compare.setMaximumSize(QSize(130, 35))
        font3 = QFont()
        font3.setFamilies([u"Calibri"])
        font3.setPointSize(20)
        font3.setBold(False)
        self.btn_compare.setFont(font3)
        self.btn_compare.setStyleSheet(u"QPushButton \n"
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

        self.horizontalLayout_2.addWidget(self.btn_compare)

        self.btn_clier = QPushButton(self.frame_btn)
        self.btn_clier.setObjectName(u"btn_clier")
        self.btn_clier.setMinimumSize(QSize(130, 35))
        self.btn_clier.setMaximumSize(QSize(130, 35))
        self.btn_clier.setFont(font3)
        self.btn_clier.setStyleSheet(u"QPushButton \n"
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

        self.horizontalLayout_2.addWidget(self.btn_clier)

        self.btn_show = QPushButton(self.frame_btn)
        self.btn_show.setObjectName(u"btn_show")
        self.btn_show.setMinimumSize(QSize(130, 35))
        self.btn_show.setMaximumSize(QSize(130, 35))
        self.btn_show.setFont(font3)
        self.btn_show.setStyleSheet(u"QPushButton \n"
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

        self.horizontalLayout_2.addWidget(self.btn_show)

        self.btn_save = QPushButton(self.frame_btn)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setMinimumSize(QSize(130, 35))
        self.btn_save.setMaximumSize(QSize(130, 35))
        self.btn_save.setFont(font3)
        self.btn_save.setStyleSheet(u"QPushButton \n"
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

        self.horizontalLayout_2.addWidget(self.btn_save)

        self.btn_print = QPushButton(self.frame_btn)
        self.btn_print.setObjectName(u"btn_print")
        self.btn_print.setMinimumSize(QSize(130, 35))
        self.btn_print.setMaximumSize(QSize(130, 35))
        self.btn_print.setFont(font3)
        self.btn_print.setStyleSheet(u"QPushButton \n"
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

        self.horizontalLayout_2.addWidget(self.btn_print)

        self.btn_exit = QPushButton(self.frame_btn)
        self.btn_exit.setObjectName(u"btn_exit")
        self.btn_exit.setMinimumSize(QSize(130, 35))
        self.btn_exit.setMaximumSize(QSize(130, 35))
        self.btn_exit.setFont(font3)
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

        self.horizontalLayout_2.addWidget(self.btn_exit)


        self.verticalLayout.addWidget(self.frame_btn)

        WindowArch.setCentralWidget(self.centralwidget)

        self.retranslateUi(WindowArch)

        self.data_stWd.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(WindowArch)
    # setupUi

    def retranslateUi(self, WindowArch):
        WindowArch.setWindowTitle(QCoreApplication.translate("WindowArch", u"Archive", None))
        self.combo_type_test.setItemText(0, QCoreApplication.translate("WindowArch", u"\u041b\u0430\u0431\u043e\u0440\u0430\u0442\u043e\u0440\u043d\u043e\u0435", None))
        self.combo_type_test.setItemText(1, QCoreApplication.translate("WindowArch", u"\u041a\u0430\u0441\u043a\u0430\u0434\u043e\u043c", None))
        self.combo_type_test.setItemText(2, QCoreApplication.translate("WindowArch", u"\u041a\u043e\u043d\u0432\u0435\u0439\u0435\u0440\u043d\u043e\u0435", None))
        self.combo_type_test.setItemText(3, QCoreApplication.translate("WindowArch", u"\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u043d\u043e\u0435", None))

        self.lbl_14.setText(QCoreApplication.translate("WindowArch", u"\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435:", None))
        self.lbl_16.setText(QCoreApplication.translate("WindowArch", u"\u041e\u043f\u0435\u0440\u0430\u0442\u043e\u0440:", None))
        self.name_le.setText("")
        self.operator_le.setText("")
        self.lbl_23.setText(QCoreApplication.translate("WindowArch", u"\u0421\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440:", None))
        self.lbl_27.setText(QCoreApplication.translate("WindowArch", u"\u0414\u0430\u0442\u0430 \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f:", None))
        self.serial_le.setText("")
        self.date_le.setText("")
        self.lbl_21.setText(QCoreApplication.translate("WindowArch", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u043e\u0442\u0431\u043e\u044f, \u043a\u0433\u0441:", None))
        self.lbl_26.setText(QCoreApplication.translate("WindowArch", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u0441\u0436\u0430\u0442\u0438\u044f, \u043a\u0433\u0441:", None))
        self.lbl_25.setText(QCoreApplication.translate("WindowArch", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f, \u043c/\u0441:", None))
        self.lbl_20.setText(QCoreApplication.translate("WindowArch", u"\u041f\u0440\u0435\u0434\u0435\u043b\u044b \u0443\u0441\u0438\u043b\u0438\u044f \u043e\u0442\u0431\u043e\u044f, \u043a\u0433\u0441:", None))
        self.lbl_17.setText(QCoreApplication.translate("WindowArch", u"\u041f\u0440\u0435\u0434\u0435\u043b\u044b \u0443\u0441\u0438\u043b\u0438\u044f \u0441\u0436\u0430\u0442\u0438\u044f, \u043a\u0433\u0441:", None))
        self.recoil_base_le.setText("")
        self.comp_base_le.setText("")
        self.speed_set_1_base_le.setText("")
        self.limit_recoil_1_base_le.setText("")
        self.limit_comp_1_base_le.setText("")
        self.power_lbl.setText(QCoreApplication.translate("WindowArch", u"\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c, \u043a\u0412\u0442:", None))
        self.power_lbl_2.setText(QCoreApplication.translate("WindowArch", u"\u0427\u0430\u0441\u0442\u043e\u0442\u0430, \u0413\u0446:", None))
        self.speed_set_2_base_le.setText("")
        self.limit_recoil_2_base_le.setText("")
        self.limit_comp_2_base_le.setText("")
        self.power_base_le.setText("")
        self.freq_base_le.setText("")
        self.lbl_22.setText(QCoreApplication.translate("WindowArch", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u043f\u043e\u0440\u0448\u043d\u044f, \u043c/\u0441:", None))
        self.lbl_24.setText(QCoreApplication.translate("WindowArch", u"\u0425\u043e\u0434 \u043f\u043e\u0440\u0448\u043d\u044f, \u043c\u043c:", None))
        self.lbl_15.setText(QCoreApplication.translate("WindowArch", u"\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u043c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f, \u00b0\u0421:", None))
        self.lbl_base_push_force.setText(QCoreApplication.translate("WindowArch", u"\u0414\u0438\u043d\u0430\u043c\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0432\u044b\u0442\u0430\u043b\u043a\u0438\u0432\u0430\u044e\u0449\u0430\u044f \u0441\u0438\u043b\u0430, \u043a\u0433\u0441:", None))
        self.speed_base_le.setText("")
        self.hod_base_le.setText("")
        self.lbl_28.setText(QCoreApplication.translate("WindowArch", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u043f\u043e\u0440\u0448\u043d\u044f, \u043c/\u0441:", None))
        self.lbl_29.setText(QCoreApplication.translate("WindowArch", u"\u0425\u043e\u0434 \u043f\u043e\u0440\u0448\u043d\u044f, \u043c\u043c:", None))
        self.lbl_18.setText(QCoreApplication.translate("WindowArch", u"\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u043c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f, \u00b0\u0421:", None))
        self.lbl_temp_push_force.setText(QCoreApplication.translate("WindowArch", u"\u0414\u0438\u043d\u0430\u043c\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0432\u044b\u0442\u0430\u043b\u043a\u0438\u0432\u0430\u044e\u0449\u0430\u044f \u0441\u0438\u043b\u0430, \u043a\u0433\u0441:", None))
        self.speed_temp_le.setText("")
        self.hod_temp_le.setText("")
        self.lbl_19.setText(QCoreApplication.translate("WindowArch", u"\u041d\u0430\u0447\u0430\u043b\u044c\u043d\u0430\u044f \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430, \u00b0\u0421:", None))
        self.lbl_30.setText(QCoreApplication.translate("WindowArch", u"\u041a\u043e\u043d\u0435\u0447\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u043e\u0442\u0431\u043e\u044f, \u043a\u0433\u0441:", None))
        self.lbl_31.setText(QCoreApplication.translate("WindowArch", u"\u041a\u043e\u043d\u0435\u0447\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u0441\u0436\u0430\u0442\u0438\u044f, \u043a\u0433\u0441:", None))
        self.recoil_end_temp_le.setText("")
        self.comp_end_temp_le.setText("")
        self.lbl_32.setText(QCoreApplication.translate("WindowArch", u"\u041d\u0430\u0447\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u043e\u0442\u0431\u043e\u044f, \u043a\u0433\u0441:", None))
        self.lbl_33.setText(QCoreApplication.translate("WindowArch", u"\u041d\u0430\u0447\u0430\u043b\u044c\u043d\u043e\u0435 \u0443\u0441\u0438\u043b\u0438\u0435 \u0441\u0436\u0430\u0442\u0438\u044f, \u043a\u0433\u0441:", None))
        self.recoil_begin_temp_le.setText("")
        self.comp_begin_temp_le.setText("")
        self.lbl_35.setText(QCoreApplication.translate("WindowArch", u"\u0425\u043e\u0434 \u043f\u043e\u0440\u0448\u043d\u044f, \u043c\u043c:", None))
        self.hod_casc_le.setText("")
        self.lbl_36.setText(QCoreApplication.translate("WindowArch", u"\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u043c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f, \u00b0\u0421:", None))
        self.lbl_casc_push_force.setText(QCoreApplication.translate("WindowArch", u"\u0414\u0438\u043d\u0430\u043c\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0432\u044b\u0442\u0430\u043b\u043a\u0438\u0432\u0430\u044e\u0449\u0430\u044f \u0441\u0438\u043b\u0430, \u043a\u0433\u0441:", None))
        ___qtablewidgetitem = self.casc_tableWt.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("WindowArch", u"1", None));
        ___qtablewidgetitem1 = self.casc_tableWt.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("WindowArch", u"2", None));
        ___qtablewidgetitem2 = self.casc_tableWt.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("WindowArch", u"3", None));
        ___qtablewidgetitem3 = self.casc_tableWt.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("WindowArch", u"4", None));
        ___qtablewidgetitem4 = self.casc_tableWt.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("WindowArch", u"5", None));
        ___qtablewidgetitem5 = self.casc_tableWt.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("WindowArch", u"6", None));
        ___qtablewidgetitem6 = self.casc_tableWt.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("WindowArch", u"7", None));
        ___qtablewidgetitem7 = self.casc_tableWt.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("WindowArch", u"8", None));
        ___qtablewidgetitem8 = self.casc_tableWt.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("WindowArch", u"9", None));
        ___qtablewidgetitem9 = self.casc_tableWt.horizontalHeaderItem(9)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("WindowArch", u"10", None));
        ___qtablewidgetitem10 = self.casc_tableWt.horizontalHeaderItem(10)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("WindowArch", u"11", None));
        ___qtablewidgetitem11 = self.casc_tableWt.horizontalHeaderItem(11)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("WindowArch", u"12", None));
        ___qtablewidgetitem12 = self.casc_tableWt.verticalHeaderItem(0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("WindowArch", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c, \u043c/\u0441", None));
        ___qtablewidgetitem13 = self.casc_tableWt.verticalHeaderItem(1)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("WindowArch", u"\u041e\u0442\u0431\u043e\u0439, \u043a\u0433\u0441", None));
        ___qtablewidgetitem14 = self.casc_tableWt.verticalHeaderItem(2)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("WindowArch", u"\u0421\u0436\u0430\u0442\u0438\u0435, \u043a\u0433\u0441", None));
        self.btn_compare.setText(QCoreApplication.translate("WindowArch", u"\u0421\u0440\u0430\u0432\u043d\u0438\u0442\u044c", None))
        self.btn_clier.setText(QCoreApplication.translate("WindowArch", u"\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c", None))
        self.btn_show.setText(QCoreApplication.translate("WindowArch", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None))
        self.btn_save.setText(QCoreApplication.translate("WindowArch", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.btn_print.setText(QCoreApplication.translate("WindowArch", u"\u041f\u0435\u0447\u0430\u0442\u044c", None))
        self.btn_exit.setText(QCoreApplication.translate("WindowArch", u"\u0412\u044b\u0445\u043e\u0434", None))
    # retranslateUi

