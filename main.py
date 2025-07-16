# -*- coding: utf-8 -*-
import sys
from tendo import singleton
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from logger import my_logger
from model import Model
from controller.controller import Controller
from wins.view import AppWindow
from wins.settings_window import SetWindow


def main():
    try:
        log = my_logger.get_logger(__name__)
        log.info('Starting program')

        me = singleton.SingleInstance()
        app = QApplication(sys.argv)
        m = Model()
        c = Controller(m)
        win_set = SetWindow(m)
        win_set.setWindowIcon(QIcon('icon/settings.png'))
        win = AppWindow(m, c, win_set)
        win.setWindowIcon(QIcon('icon/shock-absorber.png'))
        win.show()
        sys.exit(app.exec())

    except:
        print('sys.exit(0)')


if __name__ == '__main__':
    main()
