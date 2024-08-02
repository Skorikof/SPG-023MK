# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
from ui_py.new_amort import Ui_MainWindow


class AmortSignals(QObject):
    closed = pyqtSignal()
    save_amort = pyqtSignal(dict)


class AmortNew(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(AmortNew, self).__init__()
        try:
            self.setupUi(self)
            self.setWindowIcon(QIcon('icon/shock-absorber.png'))
            self.signals = AmortSignals()
            self._init_buttons()
            self.response = {}
            self.hide()
        except Exception as e:
            print(f'ERROR amorts_new/__init__ - {e}')

    def _init_buttons(self):
        self.btn_save.clicked.connect(self._save_amort)

    def init_signals(self):
        self.lineEdit_name.signal.connect(self.name_editing_finished)
        self.lineEdit_name.editingFinished.connect(self.name_editing_finished)
        self.le_length_min.signal.connect(self.len_min_editing_finished)
        self.le_length_min.editingFinished.connect(self.len_min_editing_finished)
        self.le_length_max.signal.connect(self.len_max_editing_finished)
        self.le_length_max.editingFinished.connect(self.len_max_editing_finished)
        self.le_hod.signal.connect(self.hod_editing_finished)
        self.le_hod.editingFinished.connect(self.hod_editing_finished)
        self.le_speed_one.signal.connect(self.one_speed_editing_finished)
        self.le_speed_one.editingFinished.connect(self.one_speed_editing_finished)
        self.le_speed_two.signal.connect(self.two_speed_editing_finished)
        self.le_speed_two.editingFinished.connect(self.two_speed_editing_finished)

        self.le_comp_min.signal.connect(self.comp_min_editing_finished)
        self.le_comp_min.editingFinished.connect(self.comp_min_editing_finished)
        self.le_comp_min_two.signal.connect(self.two_comp_min_editing_finished)
        self.le_comp_min_two.editingFinished.connect(self.two_comp_min_editing_finished)

        self.le_comp_max.signal.connect(self.comp_max_editing_finished)
        self.le_comp_max.editingFinished.connect(self.comp_max_editing_finished)
        self.le_comp_max_two.signal.connect(self.two_comp_max_editing_finished)
        self.le_comp_max_two.editingFinished.connect(self.two_comp_max_editing_finished)

        self.le_recoil_min.signal.connect(self.recoil_min_editing_finished)
        self.le_recoil_min.editingFinished.connect(self.recoil_min_editing_finished)
        self.le_recoil_min_two.signal.connect(self.two_recoil_min_editing_finished)
        self.le_recoil_min_two.editingFinished.connect(self.two_recoil_min_editing_finished)

        self.le_recoil_max.signal.connect(self.recoil_max_editing_finished)
        self.le_recoil_max.editingFinished.connect(self.recoil_max_editing_finished)
        self.le_recoil_max_two.signal.connect(self.two_recoil_max_editing_finished)
        self.le_recoil_max_two.editingFinished.connect(self.two_recoil_max_editing_finished)

        self.le_temper.signal.connect(self.temper_editing_finished)
        self.le_temper.editingFinished.connect(self.temper_editing_finished)
        self.response = {'name': '',
                         'len_min': '',
                         'len_max': '',
                         'hod': '',
                         'speed_one': '',
                         'speed_two': '',
                         'comp_min': '',
                         'comp_min_2': '',
                         'comp_max': '',
                         'comp_max_2': '',
                         'recoil_min': '',
                         'recoil_min_2': '',
                         'recoil_max': '',
                         'recoil_max_2': '',
                         'temper': '',
                         }

    def name_editing_finished(self):
        text = self.lineEdit_name.text()
        if not text:
            self.lineEdit_name.signal.disconnect(self.name_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          'Заполните поле названия амортизатора'
                                          )
            self.lineEdit_name.setFocus(True)
            self.lineEdit_name.signal.connect(self.name_editing_finished)
            return

        else:
            self.response['name'] = text
            # self.le_length_min.setFocus(True)

    def len_min_editing_finished(self):
        try:
            text = self.le_length_min.text()
            if not text:
                self.le_length_min.signal.disconnect(self.len_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле длины в сжатом состоянии'
                                              )
                self.le_length_min.setFocus(True)
                self.le_length_min.signal.connect(self.len_min_editing_finished)
                return

            temp = int(text)
            if 100 <= temp <= 1000:
                self.response['len_min'] = str(temp)
                # self.le_length_max.setFocus(True)
            else:
                self.le_length_min.signal.disconnect(self.len_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Длина (<b style="color: #f00;">{temp}</b>) введена некорректно'
                                              )
                self.le_length_min.setFocus(True)
                self.le_length_min.signal.connect(self.len_min_editing_finished)
                return

        except ValueError:
            self.le_length_min.signal.disconnect(self.len_min_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео некорректное значение в поле -->\n'
                                          f'длина в сжатом состоянии</b>'
                                          )
            self.le_length_min.setFocus(True)
            self.le_length_min.signal.connect(self.len_min_editing_finished)

        except Exception as e:
            pass

    def len_max_editing_finished(self):
        try:
            text = self.le_length_max.text()
            if not text:
                self.le_length_max.signal.disconnect(self.len_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле длины в разжатом состоянии'
                                              )
                self.le_length_max.setFocus(True)
                self.le_length_max.signal.connect(self.len_max_editing_finished)
                return

            temp = int(text)
            if 100 <= temp <= 1000:
                self.response['len_max'] = str(temp)
                # self.le_hod.setFocus(True)
            else:
                self.le_length_max.signal.disconnect(self.len_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Длина (<b style="color: #f00;">{temp}</b>) введена некорректно'
                                              )
                self.le_length_max.setFocus(True)
                self.le_length_max.signal.connect(self.len_max_editing_finished)
                return

        except ValueError:
            self.le_length_max.signal.disconnect(self.len_max_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Длина в разжатом состоянии</b>'
                                          )
            self.le_length_max.setFocus(True)
            self.le_length_max.signal.connect(self.len_max_editing_finished)

        except Exception as e:
            pass

    def hod_editing_finished(self):
        try:
            text = self.le_hod.text()
            if not text:
                self.le_hod.signal.disconnect(self.hod_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле испытательного хода'
                                              )
                self.le_hod.setFocus(True)
                self.le_hod.signal.connect(self.hod_editing_finished)
                return

            hod = int(text)
            if 40 <= hod <= 120:
                self.response['hod'] = str(hod)
                # self.le_speed_one.setFocus(True)
            else:
                self.le_hod.signal.disconnect(self.hod_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Ход (<b style="color: #f00;">{hod}</b>) или меньше 40 или больше 120'
                                              )
                self.le_hod.setFocus(True)
                self.le_hod.signal.connect(self.hod_editing_finished)
                return

        except ValueError:
            self.le_hod.signal.disconnect(self.hod_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле --> Ход</b>'
                                          )
            self.le_hod.setFocus(True)
            self.le_hod.signal.connect(self.hod_editing_finished)

        except Exception as e:
            pass

    def one_speed_editing_finished(self):
        try:
            text = self.le_speed_one.text()
            if not text:
                self.le_speed_one.signal.disconnect(self.one_speed_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле первой скорости испытания'
                                              )
                self.le_speed_one.setFocus(True)
                self.le_speed_one.signal.connect(self.one_speed_editing_finished)
                return

            temp = float(text.replace(',', '.'))
            max_speed = self.calculate_speed_limit()
            if 0.02 <= temp <= max_speed:
                self.response['speed_one'] = str(temp)
                # self.le_speed_two.setFocus(True)
            else:
                self.le_speed_one.signal.disconnect(self.one_speed_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Первая скорость (<b style="color: #f00;">{temp}</b>)'
                                              f'не попадает в диапазон от 0.02 до {max_speed}'
                                              )
                self.le_speed_one.setFocus(True)
                self.le_speed_one.signal.connect(self.one_speed_editing_finished)
                return

        except ValueError:
            self.le_speed_one.signal.disconnect(self.one_speed_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Первая скорость испытания</b>'
                                          )
            self.le_speed_one.setFocus(True)
            self.le_speed_one.signal.connect(self.one_speed_editing_finished)

        except Exception as e:
            pass

    def two_speed_editing_finished(self):
        try:
            text = self.le_speed_two.text()
            if not text:
                self.le_speed_two.signal.disconnect(self.two_speed_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле второй скорости испытания'
                                              )
                self.le_speed_two.setFocus(True)
                self.le_speed_two.signal.connect(self.two_speed_editing_finished)
                return

            temp = float(text.replace(',', '.'))
            max_speed = self.calculate_speed_limit()
            if 0.0 <= temp <= max_speed:
                self.response['speed_two'] = str(temp)
                # self.le_comp_min.setFocus(True)
            else:
                self.le_speed_two.signal.disconnect(self.two_speed_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Вторая скорость (<b style="color: #f00;">{temp}</b>)'
                                              f'не попадает в диапазон от 0.0 до {max_speed}'
                                              )
                self.le_speed_two.setFocus(True)
                self.le_speed_two.signal.connect(self.two_speed_editing_finished)
                return

        except ValueError:
            self.le_speed_two.signal.disconnect(self.two_speed_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Вторая скорость испытания</b>'
                                          )
            self.le_speed_two.setFocus(True)
            self.le_speed_two.signal.connect(self.two_speed_editing_finished)

        except Exception as e:
            pass

    def calculate_speed_limit(self):
        hod = int(self.response.get('hod', 40))
        if 40 <= hod < 50:
            return 0.55
        elif 50 <= hod < 60:
            return 0.7
        elif 60 <= hod < 70:
            return 0.85
        elif 70 <= hod < 80:
            return 1.0
        elif 80 <= hod < 90:
            return 1.15
        elif 90 <= hod < 100:
            return 1.3
        elif 100 <= hod < 110:
            return 1.45
        elif 110 <= hod < 120:
            return 1.6
        elif hod == 120:
            return 1.75
        else:
            return 0.55

    def comp_min_editing_finished(self):
        try:
            text = self.le_comp_min.text()
            if not text:
                self.le_comp_min.signal.disconnect(self.comp_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия сжатия'
                                              )
                self.le_comp_min.setFocus(True)
                self.le_comp_min.signal.connect(self.comp_min_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['comp_min'] = str(temp)
                # self.le_comp_max.setFocus(True)
            else:
                self.le_comp_min.signal.disconnect(self.comp_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие сжатия -- (<b style="color: #f00;">{temp}</b>) '
                                              f'введено неверное значение'
                                              )
                self.le_comp_min.setFocus(True)
                self.le_comp_min.signal.connect(self.comp_min_editing_finished)
                return

        except ValueError:
            self.le_comp_min.signal.disconnect(self.comp_min_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Минимальное усилие сжатия</b>'
                                          )
            self.le_comp_min.setFocus(True)
            self.le_comp_min.signal.connect(self.comp_min_editing_finished)

        except Exception as e:
            pass

    def two_comp_min_editing_finished(self):
        try:
            text = self.le_comp_min_two.text()
            if not text:
                self.le_comp_min_two.signal.disconnect(self.two_comp_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия сжатия для второй скорости'
                                              )
                self.le_comp_min_two.setFocus(True)
                self.le_comp_min_two.signal.connect(self.two_comp_min_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['comp_min_2'] = str(temp)
                # self.le_comp_max.setFocus(True)
            else:
                self.le_comp_min_two.signal.disconnect(self.two_comp_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие сжатия для второй скорости -- (<b style="color: #f00;">{temp}</b>)'
                                              f'введено неверное значение'
                                              )
                self.le_comp_min_two.setFocus(True)
                self.le_comp_min_two.signal.connect(self.two_comp_min_editing_finished)
                return

        except ValueError:
            self.le_comp_min_two.signal.disconnect(self.two_comp_min_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Минимальное усилие сжатия для второй скорости</b>'
                                          )
            self.le_comp_min_two.setFocus(True)
            self.le_comp_min_two.signal.connect(self.two_comp_min_editing_finished)

        except Exception as e:
            pass

    def comp_max_editing_finished(self):
        try:
            text = self.le_comp_max.text()
            if not text:
                self.le_comp_max.signal.disconnect(self.comp_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия сжатия'
                                              )
                self.le_comp_max.setFocus(True)
                self.le_comp_max.signal.connect(self.comp_max_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['comp_max'] = str(temp)
                # self.le_recoil_min.setFocus(True)
            else:
                self.le_comp_max.signal.disconnect(self.comp_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие сжатия (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неверное число'
                                              )
                self.le_comp_max.setFocus(True)
                self.le_comp_max.signal.connect(self.comp_max_editing_finished)
                return

        except ValueError:
            self.le_comp_max.signal.disconnect(self.comp_max_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Максимальное усилие сжатия</b>'
                                          )
            self.le_comp_max.setFocus(True)
            self.le_comp_max.signal.connect(self.comp_max_editing_finished)

        except Exception as e:
            pass

    def two_comp_max_editing_finished(self):
        try:
            text = self.le_comp_max_two.text()
            if not text:
                self.le_comp_max_two.signal.disconnect(self.two_comp_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия сжатия для второй скорости'
                                              )
                self.le_comp_max_two.setFocus(True)
                self.le_comp_max_two.signal.connect(self.two_comp_max_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['comp_max_2'] = str(temp)
                # self.le_recoil_min.setFocus(True)
            else:
                self.le_comp_max_two.signal.disconnect(self.two_comp_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие сжатия для второй скорости(<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неверное число'
                                              )
                self.le_comp_max_two.setFocus(True)
                self.le_comp_max_two.signal.connect(self.two_comp_max_editing_finished)
                return

        except ValueError:
            self.le_comp_max_two.signal.disconnect(self.two_comp_max_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Максимальное усилие сжатия для второй скорости</b>'
                                          )
            self.le_comp_max_two.setFocus(True)
            self.le_comp_max_two.signal.connect(self.two_comp_max_editing_finished)

        except Exception as e:
            pass

    def recoil_min_editing_finished(self):
        try:
            text = self.le_recoil_min.text()
            if not text:
                self.le_recoil_min.signal.disconnect(self.recoil_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия отбоя'
                                              )
                self.le_recoil_min.setFocus(True)
                self.le_recoil_min.signal.connect(self.recoil_min_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['recoil_min'] = str(temp)
                # self.le_recoil_max.setFocus(True)
            else:
                self.le_recoil_min.signal.disconnect(self.recoil_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие отбоя (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное число'
                                              )
                self.le_recoil_min.setFocus(True)
                self.le_recoil_min.signal.connect(self.recoil_min_editing_finished)
                return

        except ValueError:
            self.le_recoil_min.signal.disconnect(self.recoil_min_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Минимальное усилие отбоя</b>'
                                          )
            self.le_recoil_min.setFocus(True)
            self.le_recoil_min.signal.connect(self.recoil_min_editing_finished)

        except Exception as e:
            pass

    def two_recoil_min_editing_finished(self):
        try:
            text = self.le_recoil_min_two.text()
            if not text:
                self.le_recoil_min_two.signal.disconnect(self.two_recoil_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия отбоя для второй скорости'
                                              )
                self.le_recoil_min_two.setFocus(True)
                self.le_recoil_min_two.signal.connect(self.two_recoil_min_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['recoil_min_2'] = str(temp)
                # self.le_recoil_max.setFocus(True)
            else:
                self.le_recoil_min_two.signal.disconnect(self.two_recoil_min_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие отбоя для второй скорости(<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное число'
                                              )
                self.le_recoil_min_two.setFocus(True)
                self.le_recoil_min_two.signal.connect(self.two_recoil_min_editing_finished)
                return

        except ValueError:
            self.le_recoil_min_two.signal.disconnect(self.two_recoil_min_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Минимальное усилие отбоя для второй скорости</b>'
                                          )
            self.le_recoil_min_two.setFocus(True)
            self.le_recoil_min_two.signal.connect(self.two_recoil_min_editing_finished)

        except Exception as e:
            pass

    def recoil_max_editing_finished(self):
        try:
            text = self.le_recoil_max.text()
            if not text:
                self.le_recoil_max.signal.disconnect(self.recoil_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия отбоя'
                                              )
                self.le_recoil_max.setFocus(True)
                self.le_recoil_max.signal.connect(self.recoil_max_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['recoil_max'] = str(temp)
                # self.le_temper.setFocus(True)
            else:
                self.le_recoil_max.signal.disconnect(self.recoil_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие отбоя (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное значение'
                                              )
                self.le_recoil_max.setFocus(True)
                self.le_recoil_max.signal.connect(self.recoil_max_editing_finished)
                return

        except ValueError:
            self.le_recoil_max.signal.disconnect(self.recoil_max_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Максимальное усилие отбоя</b>'
                                          )
            self.le_recoil_max.setFocus(True)
            self.le_recoil_max.signal.connect(self.recoil_max_editing_finished)

        except Exception as e:
            pass

    def two_recoil_max_editing_finished(self):
        try:
            text = self.le_recoil_max_two.text()
            if not text:
                self.le_recoil_max_two.signal.disconnect(self.two_recoil_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия отбоя'
                                              )
                self.le_recoil_max_two.setFocus(True)
                self.le_recoil_max_two.signal.connect(self.two_recoil_max_editing_finished)
                return

            temp = float(text)
            if 0 <= temp <= 2000:
                self.response['recoil_max_2'] = str(temp)
                # self.le_temper.setFocus(True)
            else:
                self.le_recoil_max_two.signal.disconnect(self.two_recoil_max_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие отбоя (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное значение'
                                              )
                self.le_recoil_max_two.setFocus(True)
                self.le_recoil_max_two.signal.connect(self.two_recoil_max_editing_finished)
                return

        except ValueError:
            self.le_recoil_max_two.signal.disconnect(self.two_recoil_max_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Максимальное усилие отбоя</b>'
                                          )
            self.le_recoil_max_two.setFocus(True)
            self.le_recoil_max_two.signal.connect(self.two_recoil_max_editing_finished)

        except Exception as e:
            pass

    def temper_editing_finished(self):
        try:
            text = self.le_temper.text()
            if not text:
                self.le_temper.signal.disconnect(self.temper_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимальной температуры'
                                              )
                self.le_temper.setFocus(True)
                self.le_temper.signal.connect(self.temper_editing_finished)
                return

            temp = int(text)
            if 0 <= temp <= 120:
                self.response['temper'] = str(temp)
                # self.lineEdit_name.setFocus(True)
            else:
                self.le_temper.signal.disconnect(self.temper_editing_finished)
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальная температура (<b style="color: #f00;">{temp}</b>) '
                                              f'или меньше 0 или больше 120'
                                              )
                self.le_temper.setFocus(True)
                self.le_temper.signal.connect(self.temper_editing_finished)
                return

        except ValueError:
            self.le_temper.signal.disconnect(self.temper_editing_finished)
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введенео не корректное значение в поле -->\n'
                                          f'Максимальная температура</b>'
                                          )
            self.le_temper.setFocus(True)
            self.le_temper.signal.connect(self.temper_editing_finished)

        except Exception as e:
            pass

    def closeEvent(self, event):
        self.lineEdit_name.signal.disconnect(self.name_editing_finished)
        self.lineEdit_name.editingFinished.disconnect(self.name_editing_finished)
        self.le_length_min.signal.disconnect(self.len_min_editing_finished)
        self.le_length_min.editingFinished.disconnect(self.len_min_editing_finished)
        self.le_length_max.signal.disconnect(self.len_max_editing_finished)
        self.le_length_max.editingFinished.disconnect(self.len_max_editing_finished)
        self.le_hod.signal.disconnect(self.hod_editing_finished)
        self.le_hod.editingFinished.disconnect(self.hod_editing_finished)
        self.le_speed_one.signal.disconnect(self.one_speed_editing_finished)
        self.le_speed_one.editingFinished.disconnect(self.one_speed_editing_finished)
        self.le_speed_two.signal.disconnect(self.two_speed_editing_finished)
        self.le_speed_two.editingFinished.disconnect(self.two_speed_editing_finished)

        self.le_comp_min.signal.disconnect(self.comp_min_editing_finished)
        self.le_comp_min.editingFinished.disconnect(self.comp_min_editing_finished)
        self.le_comp_min_two.signal.disconnect(self.two_comp_min_editing_finished)
        self.le_comp_min_two.editingFinished.disconnect(self.two_comp_min_editing_finished)

        self.le_comp_max.signal.disconnect(self.comp_max_editing_finished)
        self.le_comp_max.editingFinished.disconnect(self.comp_max_editing_finished)
        self.le_comp_max_two.signal.disconnect(self.two_comp_max_editing_finished)
        self.le_comp_max_two.editingFinished.disconnect(self.two_comp_max_editing_finished)

        self.le_recoil_min.signal.disconnect(self.recoil_min_editing_finished)
        self.le_recoil_min.editingFinished.disconnect(self.recoil_min_editing_finished)
        self.le_recoil_min_two.signal.disconnect(self.two_recoil_min_editing_finished)
        self.le_recoil_min_two.editingFinished.disconnect(self.two_recoil_min_editing_finished)

        self.le_recoil_max.signal.disconnect(self.recoil_max_editing_finished)
        self.le_recoil_max.editingFinished.disconnect(self.recoil_max_editing_finished)
        self.le_recoil_max_two.signal.disconnect(self.two_recoil_max_editing_finished)
        self.le_recoil_max_two.editingFinished.disconnect(self.two_recoil_max_editing_finished)

        self.le_temper.signal.disconnect(self.temper_editing_finished)
        self.le_temper.editingFinished.disconnect(self.temper_editing_finished)

        self.signals.closed.emit()

    def _save_amort(self):
        try:
            flag = True
            for key, value in self.response.items():
                if value != '':
                    pass
                else:
                    flag = False
                    msg = QMessageBox.information(self,
                                                  'Внимание',
                                                  f'Проверьте введённые параметры\n'
                                                  f'Какой-то введён некорректно'
                                                  )
                    self.lineEdit_name.setFocus(True)
                    break

            if flag:
                self.response['adapter'] = self.adapter_cb.currentText()
                self.signals.save_amort.emit(self.response)

            else:
                pass
        except Exception as e:
            print(f'ERROR amorts_new/_save_amort - {e}')
