# -*- coding: utf-8 -*-
import sys
from tendo import singleton
from PyQt5.QtWidgets import QApplication

from logger import my_logger
from wins.archive_win import ArchiveWin


def main():
    try:
        me = singleton.SingleInstance()
        log = my_logger.get_logger(__name__)
        log.info('Starting view archive')

        app = QApplication(sys.argv)

        win = ArchiveWin()
        win.init_archive_win()
        win.show()
        sys.exit(app.exec_())

    except:
        print('sys.exit(0)')
        sys.exit(0)


if __name__ == '__main__':
    main()