# -*- coding: utf-8 -*-
import sys
from tendo import singleton
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app.wins.view import AppWindow
from scripts.controller.controller import Controller
from scripts.logger import my_logger
from scripts.model import Model


def main():
    try:
        log = my_logger.get_logger(__name__)
        log.debug('Starting program')

        me = singleton.SingleInstance()
        app = QApplication(sys.argv)
        m = Model()
        c = Controller(m)
        win = AppWindow(m, c)
        win.setWindowIcon(QIcon('icon/shock-absorber.png'))
        win.show()
        sys.exit(app.exec())

    except:
        log.debug('sys.exit(0)')
        sys.exit(0)


if __name__ == '__main__':
    main()
