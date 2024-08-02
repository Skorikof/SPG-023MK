# -*- coding: utf-8 -*-
import sys
from model import Model
from controller import Controller
from wins.view import AppWindow
from wins.settings_window import SetWindow
from tendo import singleton
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon


def main():
    try:
        me = singleton.SingleInstance()
        app = QApplication(sys.argv)
        m = Model()
        c = Controller(m)
        win_set = SetWindow(m)
        win_set.setWindowIcon(QIcon('icon/settings.png'))
        win = AppWindow(m, c, win_set)
        win.setWindowIcon(QIcon('icon/shock-absorber.png'))
        win.show()
        sys.exit(app.exec_())

    except:
        print('sys.exit(0)')
        sys.exit(0)


if __name__ == '__main__':
    main()
