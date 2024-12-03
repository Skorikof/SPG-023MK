# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
from ui_py.new_amort import Ui_MainWindow
from my_obj.data_calculation import SpeedLimitForHod


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
            print(f'ERROR in amorts_new/__init__ - {e}')

    def start_param_new_amort(self):
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

    def _init_buttons(self):
        self.btn_save.clicked.connect(self._save_amort)

    def name_editing_finished(self):
        text = self.lineEdit_name.text()
        if not text:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          'Заполните поле названия амортизатора'
                                          )
            self.response['name'] = ''

        else:
            self.response['name'] = text

    def len_min_editing_finished(self):
        try:
            text = self.le_length_min.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле длины в сжатом состоянии'
                                              )
                self.response['len_min'] = ''

            temp = float(text.replace(',', '.'))
            if 100 <= temp <= 1000:
                self.response['len_min'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Длина (<b style="color: #f00;">{temp}</b>) введена некорректно'
                                              )
                self.response['len_min'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено некорректное значение в поле -->\n'
                                          f'длина в сжатом состоянии</b>'
                                          )
            self.response['len_min'] = ''

        except Exception as e:
            pass

    def len_max_editing_finished(self):
        try:
            text = self.le_length_max.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле длины в разжатом состоянии'
                                              )
                self.response['len_max'] = ''

            temp = float(text.replace(',', '.'))
            if 100 <= temp <= 1000:
                self.response['len_max'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Длина (<b style="color: #f00;">{temp}</b>) введена некорректно'
                                              )
                self.response['len_max'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Длина в разжатом состоянии</b>'
                                          )
            self.response['len_max'] = ''

        except Exception as e:
            pass

    def hod_editing_finished(self):
        try:
            text = self.le_hod.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле испытательного хода'
                                              )
                self.response['hod'] = ''

            hod = int(text)
            if 40 <= hod <= 120:
                self.response['hod'] = str(hod)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Ход (<b style="color: #f00;">{hod}</b>) или меньше 40 или больше 120'
                                              )
                self.response['hod'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле --> Ход</b>'
                                          )
            self.response['hod'] = ''

        except Exception as e:
            pass

    def one_speed_editing_finished(self):
        try:
            text = self.le_speed_one.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле первой скорости испытания'
                                              )
                self.response['speed_one'] = ''

            temp = float(text.replace(',', '.'))

            hod = int(self.response.get('hod', 40))
            max_speed = SpeedLimitForHod().calculate_speed_limit(hod)

            if 0.02 <= temp <= max_speed:
                self.response['speed_one'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Первая скорость (<b style="color: #f00;">{temp}</b>)'
                                              f'не попадает в диапазон от 0.02 до {max_speed}'
                                              )
                self.response['speed_one'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Первая скорость испытания</b>'
                                          )
            self.response['speed_one'] = ''

        except Exception as e:
            pass

    def two_speed_editing_finished(self):
        try:
            text = self.le_speed_two.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле второй скорости испытания'
                                              )
                self.response['speed_two'] = ''

            temp = float(text.replace(',', '.'))

            hod = int(self.response.get('hod', 40))
            max_speed = SpeedLimitForHod().calculate_speed_limit(hod)

            if 0.02 <= temp <= max_speed:
                self.response['speed_two'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Вторая скорость (<b style="color: #f00;">{temp}</b>)'
                                              f'не попадает в диапазон от 0.02 до {max_speed}'
                                              )
                self.response['speed_two'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Вторая скорость испытания</b>'
                                          )
            self.response['speed_two'] = ''

        except Exception as e:
            pass

    def comp_min_editing_finished(self):
        try:
            text = self.le_comp_min.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия сжатия'
                                              )
                self.response['comp_min'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['comp_min'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие сжатия --> (<b style="color: #f00;">{temp}</b>) '
                                              f'введено неверное значение'
                                              )
                self.response['comp_min'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Минимальное усилие сжатия</b>'
                                          )
            self.response['comp_min'] = ''

        except Exception as e:
            pass

    def two_comp_min_editing_finished(self):
        try:
            text = self.le_comp_min_two.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия сжатия для второй скорости'
                                              )
                self.response['comp_min_2'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['comp_min_2'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие сжатия для второй скорости --> (<b style="color: #f00;">{temp}</b>)'
                                              f'введено неверное значение'
                                              )
                self.response['comp_min_2'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Минимальное усилие сжатия для второй скорости</b>'
                                          )
            self.response['comp_min_2'] = ''

        except Exception as e:
            pass

    def comp_max_editing_finished(self):
        try:
            text = self.le_comp_max.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия сжатия'
                                              )
                self.response['comp_max'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['comp_max'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие сжатия (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неверное число'
                                              )
                self.response['comp_max'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Максимальное усилие сжатия</b>'
                                          )
            self.response['comp_max'] = ''

        except Exception as e:
            pass

    def two_comp_max_editing_finished(self):
        try:
            text = self.le_comp_max_two.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия сжатия для второй скорости'
                                              )
                self.response['comp_max_2'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['comp_max_2'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие сжатия для второй скорости(<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неверное число'
                                              )
                self.response['comp_max_2'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Максимальное усилие сжатия для второй скорости</b>'
                                          )
            self.response['comp_max_2'] = ''

        except Exception as e:
            pass

    def recoil_min_editing_finished(self):
        try:
            text = self.le_recoil_min.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия отбоя'
                                              )
                self.response['recoil_min'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['recoil_min'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие отбоя (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное число'
                                              )
                self.response['recoil_min'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Минимальное усилие отбоя</b>'
                                          )
            self.response['recoil_min'] = ''

        except Exception as e:
            pass

    def two_recoil_min_editing_finished(self):
        try:
            text = self.le_recoil_min_two.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле минимального усилия отбоя для второй скорости'
                                              )
                self.response['recoil_min_2'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['recoil_min_2'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Минимальное усилие отбоя для второй скорости(<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное число'
                                              )
                self.response['recoil_min_2'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Минимальное усилие отбоя для второй скорости</b>'
                                          )
            self.response['recoil_min_2'] = ''

        except Exception as e:
            pass

    def recoil_max_editing_finished(self):
        try:
            text = self.le_recoil_max.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия отбоя'
                                              )
                self.response['recoil_max'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['recoil_max'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие отбоя (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное значение'
                                              )
                self.response['recoil_max'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Максимальное усилие отбоя</b>'
                                          )
            self.response['recoil_max'] = ''

        except Exception as e:
            pass

    def two_recoil_max_editing_finished(self):
        try:
            text = self.le_recoil_max_two.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимального усилия отбоя'
                                              )
                self.response['recoil_max_2'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 2000:
                self.response['recoil_max_2'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальное усилие отбоя (<b style="color: #f00;">{temp}</b>)\n'
                                              f'введено неправильное значение'
                                              )
                self.response['recoil_max_2'] = ''

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Максимальное усилие отбоя</b>'
                                          )
            self.response['recoil_max_2'] = ''

        except Exception as e:
            pass

    def temper_editing_finished(self):
        try:
            text = self.le_temper.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимальной температуры'
                                              )
                self.response['temper'] = ''

            temp = float(text.replace(',', '.'))
            if 0 <= temp <= 120:
                self.response['temper'] = str(temp)
            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Максимальная температура (<b style="color: #f00;">{temp}</b>) '
                                              f'или меньше 0 или больше 120'
                                              )

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено не корректное значение в поле -->\n'
                                          f'Максимальная температура</b>'
                                          )
            self.response['temper'] = ''

        except Exception as e:
            pass

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _read_data_from_gui(self):
        self.name_editing_finished()
        self.len_min_editing_finished()
        self.len_max_editing_finished()
        self.hod_editing_finished()
        self.one_speed_editing_finished()
        self.two_speed_editing_finished()
        self.comp_min_editing_finished()
        self.two_comp_min_editing_finished()
        self.comp_max_editing_finished()
        self.two_comp_max_editing_finished()
        self.recoil_min_editing_finished()
        self.two_recoil_min_editing_finished()
        self.recoil_max_editing_finished()
        self.two_recoil_max_editing_finished()
        self.temper_editing_finished()

    def _clear_data_on_gui(self):
        self.lineEdit_name.clear()
        self.le_length_min.clear()
        self.le_length_max.clear()
        self.le_hod.clear()
        self.le_speed_one.clear()
        self.le_speed_two.clear()
        self.le_comp_min.clear()
        self.le_comp_min_two.clear()
        self.le_comp_max.clear()
        self.le_comp_max_two.clear()
        self.le_recoil_min.clear()
        self.le_recoil_min_two.clear()
        self.le_recoil_max.clear()
        self.le_recoil_max_two.clear()
        self.le_temper.clear()

    def _save_amort(self):
        try:
            self._read_data_from_gui()
            flag = True
            for key, value in self.response.items():
                if value != '':
                    pass
                else:
                    flag = False
                    break

            if flag:
                self.response['adapter'] = self.adapter_cb.currentText()
                self._clear_data_on_gui()
                self.signals.save_amort.emit(self.response)

            else:
                pass

        except Exception as e:
            print(f'ERROR amorts_new/_save_amort - {e}')
