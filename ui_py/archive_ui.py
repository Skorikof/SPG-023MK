# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'archive_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WindowArch(object):
    def setupUi(self, WindowArch):
        WindowArch.setObjectName("WindowArch")
        WindowArch.resize(1024, 940)
        WindowArch.setMinimumSize(QtCore.QSize(1024, 940))
        WindowArch.setMaximumSize(QtCore.QSize(1024, 940))
        WindowArch.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(WindowArch)
        self.centralwidget.setMinimumSize(QtCore.QSize(1024, 920))
        self.centralwidget.setMaximumSize(QtCore.QSize(1024, 920))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_title = QtWidgets.QFrame(self.centralwidget)
        self.frame_title.setMinimumSize(QtCore.QSize(0, 40))
        self.frame_title.setMaximumSize(QtCore.QSize(16777215, 40))
        self.frame_title.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_title.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_title.setObjectName("frame_title")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_title)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.combo_dates = QtWidgets.QComboBox(self.frame_title)
        self.combo_dates.setMinimumSize(QtCore.QSize(150, 30))
        self.combo_dates.setMaximumSize(QtCore.QSize(150, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.combo_dates.setFont(font)
        self.combo_dates.setObjectName("combo_dates")
        self.horizontalLayout.addWidget(self.combo_dates)
        self.combo_test = QtWidgets.QComboBox(self.frame_title)
        self.combo_test.setMinimumSize(QtCore.QSize(500, 30))
        self.combo_test.setMaximumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.combo_test.setFont(font)
        self.combo_test.setObjectName("combo_test")
        self.horizontalLayout.addWidget(self.combo_test)
        self.combo_type = QtWidgets.QComboBox(self.frame_title)
        self.combo_type.setMinimumSize(QtCore.QSize(250, 30))
        self.combo_type.setMaximumSize(QtCore.QSize(250, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.combo_type.setFont(font)
        self.combo_type.setObjectName("combo_type")
        self.combo_type.addItem("")
        self.combo_type.addItem("")
        self.horizontalLayout.addWidget(self.combo_type)
        self.verticalLayout.addWidget(self.frame_title)
        self.frame_content = QtWidgets.QFrame(self.centralwidget)
        self.frame_content.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.frame_content.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_content.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_content.setObjectName("frame_content")
        self.graphwidget = PlotWidget(self.frame_content)
        self.graphwidget.setGeometry(QtCore.QRect(10, 10, 1000, 530))
        self.graphwidget.setMinimumSize(QtCore.QSize(0, 530))
        self.graphwidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.graphwidget.setAutoFillBackground(False)
        self.graphwidget.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.graphwidget.setObjectName("graphwidget")
        self.test_data_frame = QtWidgets.QFrame(self.frame_content)
        self.test_data_frame.setGeometry(QtCore.QRect(10, 540, 1000, 290))
        self.test_data_frame.setMinimumSize(QtCore.QSize(1000, 290))
        self.test_data_frame.setMaximumSize(QtCore.QSize(1000, 290))
        self.test_data_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.test_data_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.test_data_frame.setObjectName("test_data_frame")
        self.serial_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.serial_le.setGeometry(QtCore.QRect(840, 10, 150, 30))
        self.serial_le.setMinimumSize(QtCore.QSize(150, 30))
        self.serial_le.setMaximumSize(QtCore.QSize(150, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.serial_le.setFont(font)
        self.serial_le.setText("")
        self.serial_le.setAlignment(QtCore.Qt.AlignCenter)
        self.serial_le.setReadOnly(True)
        self.serial_le.setObjectName("serial_le")
        self.lbl_17 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_17.setGeometry(QtCore.QRect(10, 170, 216, 30))
        self.lbl_17.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_17.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_17.setFont(font)
        self.lbl_17.setObjectName("lbl_17")
        self.lbl_14 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_14.setGeometry(QtCore.QRect(10, 10, 121, 30))
        self.lbl_14.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_14.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_14.setFont(font)
        self.lbl_14.setObjectName("lbl_14")
        self.lbl_20 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_20.setGeometry(QtCore.QRect(10, 130, 208, 30))
        self.lbl_20.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_20.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_20.setFont(font)
        self.lbl_20.setObjectName("lbl_20")
        self.name_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.name_le.setGeometry(QtCore.QRect(275, 10, 350, 30))
        self.name_le.setMinimumSize(QtCore.QSize(350, 30))
        self.name_le.setMaximumSize(QtCore.QSize(350, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.name_le.setFont(font)
        self.name_le.setText("")
        self.name_le.setAlignment(QtCore.Qt.AlignCenter)
        self.name_le.setReadOnly(True)
        self.name_le.setObjectName("name_le")
        self.lbl_23 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_23.setGeometry(QtCore.QRect(640, 10, 128, 30))
        self.lbl_23.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_23.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_23.setFont(font)
        self.lbl_23.setObjectName("lbl_23")
        self.limit_recoil_1_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.limit_recoil_1_le.setGeometry(QtCore.QRect(275, 130, 140, 30))
        self.limit_recoil_1_le.setMinimumSize(QtCore.QSize(140, 30))
        self.limit_recoil_1_le.setMaximumSize(QtCore.QSize(140, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.limit_recoil_1_le.setFont(font)
        self.limit_recoil_1_le.setText("")
        self.limit_recoil_1_le.setAlignment(QtCore.Qt.AlignCenter)
        self.limit_recoil_1_le.setReadOnly(True)
        self.limit_recoil_1_le.setObjectName("limit_recoil_1_le")
        self.limit_comp_1_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.limit_comp_1_le.setGeometry(QtCore.QRect(275, 170, 140, 30))
        self.limit_comp_1_le.setMinimumSize(QtCore.QSize(140, 30))
        self.limit_comp_1_le.setMaximumSize(QtCore.QSize(140, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.limit_comp_1_le.setFont(font)
        self.limit_comp_1_le.setText("")
        self.limit_comp_1_le.setAlignment(QtCore.Qt.AlignCenter)
        self.limit_comp_1_le.setReadOnly(True)
        self.limit_comp_1_le.setObjectName("limit_comp_1_le")
        self.lbl_15 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_15.setGeometry(QtCore.QRect(640, 130, 235, 30))
        self.lbl_15.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_15.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_15.setFont(font)
        self.lbl_15.setObjectName("lbl_15")
        self.max_temp_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.max_temp_le.setGeometry(QtCore.QRect(880, 130, 80, 30))
        self.max_temp_le.setMinimumSize(QtCore.QSize(80, 30))
        self.max_temp_le.setMaximumSize(QtCore.QSize(80, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.max_temp_le.setFont(font)
        self.max_temp_le.setAlignment(QtCore.Qt.AlignCenter)
        self.max_temp_le.setReadOnly(True)
        self.max_temp_le.setObjectName("max_temp_le")
        self.lbl_22 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_22.setGeometry(QtCore.QRect(640, 90, 211, 30))
        self.lbl_22.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_22.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_22.setFont(font)
        self.lbl_22.setObjectName("lbl_22")
        self.speed_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.speed_le.setGeometry(QtCore.QRect(880, 90, 80, 30))
        self.speed_le.setMinimumSize(QtCore.QSize(80, 30))
        self.speed_le.setMaximumSize(QtCore.QSize(80, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.speed_le.setFont(font)
        self.speed_le.setText("")
        self.speed_le.setAlignment(QtCore.Qt.AlignCenter)
        self.speed_le.setReadOnly(False)
        self.speed_le.setObjectName("speed_le")
        self.lbl_24 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_24.setGeometry(QtCore.QRect(640, 170, 186, 30))
        self.lbl_24.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_24.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_24.setFont(font)
        self.lbl_24.setObjectName("lbl_24")
        self.hod_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.hod_le.setGeometry(QtCore.QRect(880, 170, 80, 30))
        self.hod_le.setMinimumSize(QtCore.QSize(80, 30))
        self.hod_le.setMaximumSize(QtCore.QSize(80, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.hod_le.setFont(font)
        self.hod_le.setText("")
        self.hod_le.setAlignment(QtCore.Qt.AlignCenter)
        self.hod_le.setReadOnly(True)
        self.hod_le.setObjectName("hod_le")
        self.lbl_18 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_18.setGeometry(QtCore.QRect(640, 210, 216, 30))
        self.lbl_18.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_18.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_18.setFont(font)
        self.lbl_18.setObjectName("lbl_18")
        self.push_force_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.push_force_le.setGeometry(QtCore.QRect(880, 210, 80, 30))
        self.push_force_le.setMinimumSize(QtCore.QSize(80, 30))
        self.push_force_le.setMaximumSize(QtCore.QSize(80, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.push_force_le.setFont(font)
        self.push_force_le.setText("")
        self.push_force_le.setAlignment(QtCore.Qt.AlignCenter)
        self.push_force_le.setReadOnly(True)
        self.push_force_le.setObjectName("push_force_le")
        self.lbl_25 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_25.setGeometry(QtCore.QRect(10, 90, 211, 30))
        self.lbl_25.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_25.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_25.setFont(font)
        self.lbl_25.setObjectName("lbl_25")
        self.speed_set_1_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.speed_set_1_le.setGeometry(QtCore.QRect(275, 90, 80, 30))
        self.speed_set_1_le.setMinimumSize(QtCore.QSize(80, 30))
        self.speed_set_1_le.setMaximumSize(QtCore.QSize(80, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.speed_set_1_le.setFont(font)
        self.speed_set_1_le.setText("")
        self.speed_set_1_le.setAlignment(QtCore.Qt.AlignCenter)
        self.speed_set_1_le.setReadOnly(True)
        self.speed_set_1_le.setObjectName("speed_set_1_le")
        self.speed_set_2_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.speed_set_2_le.setGeometry(QtCore.QRect(430, 90, 80, 30))
        self.speed_set_2_le.setMinimumSize(QtCore.QSize(80, 30))
        self.speed_set_2_le.setMaximumSize(QtCore.QSize(80, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.speed_set_2_le.setFont(font)
        self.speed_set_2_le.setText("")
        self.speed_set_2_le.setAlignment(QtCore.Qt.AlignCenter)
        self.speed_set_2_le.setReadOnly(True)
        self.speed_set_2_le.setObjectName("speed_set_2_le")
        self.limit_recoil_2_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.limit_recoil_2_le.setGeometry(QtCore.QRect(430, 130, 140, 30))
        self.limit_recoil_2_le.setMinimumSize(QtCore.QSize(140, 30))
        self.limit_recoil_2_le.setMaximumSize(QtCore.QSize(140, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.limit_recoil_2_le.setFont(font)
        self.limit_recoil_2_le.setText("")
        self.limit_recoil_2_le.setAlignment(QtCore.Qt.AlignCenter)
        self.limit_recoil_2_le.setReadOnly(True)
        self.limit_recoil_2_le.setObjectName("limit_recoil_2_le")
        self.limit_comp_2_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.limit_comp_2_le.setGeometry(QtCore.QRect(430, 170, 140, 30))
        self.limit_comp_2_le.setMinimumSize(QtCore.QSize(140, 30))
        self.limit_comp_2_le.setMaximumSize(QtCore.QSize(140, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.limit_comp_2_le.setFont(font)
        self.limit_comp_2_le.setText("")
        self.limit_comp_2_le.setAlignment(QtCore.Qt.AlignCenter)
        self.limit_comp_2_le.setReadOnly(True)
        self.limit_comp_2_le.setObjectName("limit_comp_2_le")
        self.lbl_21 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_21.setGeometry(QtCore.QRect(170, 210, 250, 30))
        self.lbl_21.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_21.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_21.setFont(font)
        self.lbl_21.setObjectName("lbl_21")
        self.lbl_26 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_26.setGeometry(QtCore.QRect(170, 250, 250, 30))
        self.lbl_26.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_26.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_26.setFont(font)
        self.lbl_26.setObjectName("lbl_26")
        self.recoil_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.recoil_le.setGeometry(QtCore.QRect(430, 210, 100, 30))
        self.recoil_le.setMinimumSize(QtCore.QSize(100, 30))
        self.recoil_le.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.recoil_le.setFont(font)
        self.recoil_le.setText("")
        self.recoil_le.setAlignment(QtCore.Qt.AlignCenter)
        self.recoil_le.setReadOnly(True)
        self.recoil_le.setObjectName("recoil_le")
        self.comp_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.comp_le.setGeometry(QtCore.QRect(430, 250, 100, 30))
        self.comp_le.setMinimumSize(QtCore.QSize(100, 30))
        self.comp_le.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.comp_le.setFont(font)
        self.comp_le.setText("")
        self.comp_le.setAlignment(QtCore.Qt.AlignCenter)
        self.comp_le.setReadOnly(True)
        self.comp_le.setObjectName("comp_le")
        self.lbl_push_force = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_push_force.setGeometry(QtCore.QRect(10, 210, 141, 71))
        self.lbl_push_force.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_push_force.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_push_force.setFont(font)
        self.lbl_push_force.setTextFormat(QtCore.Qt.AutoText)
        self.lbl_push_force.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_push_force.setObjectName("lbl_push_force")
        self.lbl_27 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_27.setGeometry(QtCore.QRect(640, 50, 128, 30))
        self.lbl_27.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_27.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_27.setFont(font)
        self.lbl_27.setObjectName("lbl_27")
        self.date_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.date_le.setGeometry(QtCore.QRect(770, 50, 220, 30))
        self.date_le.setMinimumSize(QtCore.QSize(220, 30))
        self.date_le.setMaximumSize(QtCore.QSize(220, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.date_le.setFont(font)
        self.date_le.setText("")
        self.date_le.setAlignment(QtCore.Qt.AlignCenter)
        self.date_le.setReadOnly(True)
        self.date_le.setObjectName("date_le")
        self.lbl_16 = QtWidgets.QLabel(self.test_data_frame)
        self.lbl_16.setGeometry(QtCore.QRect(10, 50, 121, 30))
        self.lbl_16.setMinimumSize(QtCore.QSize(0, 30))
        self.lbl_16.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lbl_16.setFont(font)
        self.lbl_16.setObjectName("lbl_16")
        self.operator_le = QtWidgets.QLineEdit(self.test_data_frame)
        self.operator_le.setGeometry(QtCore.QRect(275, 50, 350, 30))
        self.operator_le.setMinimumSize(QtCore.QSize(350, 30))
        self.operator_le.setMaximumSize(QtCore.QSize(350, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.operator_le.setFont(font)
        self.operator_le.setText("")
        self.operator_le.setAlignment(QtCore.Qt.AlignCenter)
        self.operator_le.setReadOnly(True)
        self.operator_le.setObjectName("operator_le")
        self.verticalLayout.addWidget(self.frame_content)
        self.frame_btn = QtWidgets.QFrame(self.centralwidget)
        self.frame_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.frame_btn.setMaximumSize(QtCore.QSize(16777215, 50))
        self.frame_btn.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_btn.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_btn.setObjectName("frame_btn")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_btn)
        self.horizontalLayout_2.setContentsMargins(10, 5, 10, 10)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_print = QtWidgets.QPushButton(self.frame_btn)
        self.btn_print.setMinimumSize(QtCore.QSize(220, 35))
        self.btn_print.setMaximumSize(QtCore.QSize(220, 35))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.btn_print.setFont(font)
        self.btn_print.setStyleSheet("QPushButton \n"
"{\n"
"    color: rgb(0, 0, 0);\n"
"    background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"    border: 1px rgb(0, 0, 0);\n"
"    border-radius: 10px;\n"
"\n"
"    border-style: outset;\n"
"\n"
"    padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"    background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"    \n"
"}\n"
"    \n"
"\n"
"QPushButton:checked\n"
"{\n"
"    \n"
"    background-color: rgb(0, 0, 255);\n"
"    \n"
"}")
        self.btn_print.setObjectName("btn_print")
        self.horizontalLayout_2.addWidget(self.btn_print)
        self.btn_exit = QtWidgets.QPushButton(self.frame_btn)
        self.btn_exit.setMinimumSize(QtCore.QSize(220, 35))
        self.btn_exit.setMaximumSize(QtCore.QSize(220, 35))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.btn_exit.setFont(font)
        self.btn_exit.setStyleSheet("QPushButton \n"
"{\n"
"    color: rgb(0, 0, 0);\n"
"    background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"    border: 1px rgb(0, 0, 0);\n"
"    border-radius: 10px;\n"
"\n"
"    border-style: outset;\n"
"\n"
"    padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"    background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"    \n"
"}\n"
"    \n"
"\n"
"QPushButton:checked\n"
"{\n"
"    \n"
"    background-color: rgb(0, 0, 255);\n"
"    \n"
"}")
        self.btn_exit.setObjectName("btn_exit")
        self.horizontalLayout_2.addWidget(self.btn_exit)
        self.verticalLayout.addWidget(self.frame_btn)
        WindowArch.setCentralWidget(self.centralwidget)

        self.retranslateUi(WindowArch)
        QtCore.QMetaObject.connectSlotsByName(WindowArch)

    def retranslateUi(self, WindowArch):
        _translate = QtCore.QCoreApplication.translate
        WindowArch.setWindowTitle(_translate("WindowArch", "Archive"))
        self.combo_type.setItemText(0, _translate("WindowArch", "Перемещение / Усилие"))
        self.combo_type.setItemText(1, _translate("WindowArch", "Усилие / Скорость"))
        self.lbl_17.setText(_translate("WindowArch", "Пределы усилия сжатия, кгс:"))
        self.lbl_14.setText(_translate("WindowArch", "Наименование:"))
        self.lbl_20.setText(_translate("WindowArch", "Пределы усилия отбоя, кгс:"))
        self.lbl_23.setText(_translate("WindowArch", "Серийный номер:"))
        self.lbl_15.setText(_translate("WindowArch", "Температура максимальная, °С:"))
        self.lbl_22.setText(_translate("WindowArch", "Скорость текущая, м/с:"))
        self.lbl_24.setText(_translate("WindowArch", "Ход исытания, мм:"))
        self.lbl_18.setText(_translate("WindowArch", "Выталкивающая сила, кгс:"))
        self.lbl_25.setText(_translate("WindowArch", "Скорость испытания, м/с:"))
        self.lbl_21.setText(_translate("WindowArch", "Максимальное усилие отбоя, кгс:"))
        self.lbl_26.setText(_translate("WindowArch", "Максимальное усилие сжатия, кгс:"))
        self.lbl_push_force.setText(_translate("WindowArch", "Выталкивающая\n"
"сила\n"
"учитываетcя"))
        self.lbl_27.setText(_translate("WindowArch", "Дата испытания:"))
        self.lbl_16.setText(_translate("WindowArch", "Оператор:"))
        self.btn_print.setText(_translate("WindowArch", "Печать"))
        self.btn_exit.setText(_translate("WindowArch", "Выход"))
from pyqtgraph import PlotWidget
