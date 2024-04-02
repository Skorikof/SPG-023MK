import sys
from model import Model
from controller import Controller
from view import AppWindow
from settings_window import SetWindow
from tendo import singleton
from PyQt5.QtWidgets import QApplication


def main():
    try:
        me = singleton.SingleInstance()
        app = QApplication(sys.argv)
        m = Model()
        c = Controller(m)
        win_set = SetWindow(m)
        win = AppWindow(m, c)
        win.show()
        sys.exit(app.exec_())

    except:
        print('sys.exit(0)')
        sys.exit(0)


if __name__ == '__main__':
    main()
