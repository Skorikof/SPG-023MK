# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal

from app.ui_py.new_amort import Ui_NewAmortWindow
from scripts.data_calculation import CalcData
from scripts.logger import my_logger


class AmortSignals(QObject):
    closed = Signal()
    save_amort = Signal(dict)


class AmortNew(QMainWindow, Ui_NewAmortWindow):
    def __init__(self):
        super(AmortNew, self).__init__()
        try:
            self.logger = my_logger.get_logger(__name__)
            self.setupUi(self)
            self.setWindowIcon(QIcon('icon/shock-absorber.png'))
            self.signals = AmortSignals()
            self.calc_data = CalcData()
            self.response = self._get_empty_response()
            self._init_buttons()
            self.hide()
            
        except Exception as e:
            self.logger.error(e)
            
    def _get_empty_response(self):
        return {
            'tag': 'new',
            'name': '',
            'min_length': '',
            'max_length': '',
            'hod': '',
            'speed_one': '',
            'speed_two': '',
            'min_comp': '',
            'min_comp_2': '',
            'max_comp': '',
            'max_comp_2': '',
            'min_recoil': '',
            'min_recoil_2': '',
            'max_recoil': '',
            'max_recoil_2': '',
            'max_temper': '',
            'adapter': '',
            'adapter_len': 0
        }

    def _init_buttons(self):
        self.btn_save.clicked.connect(self._save_amort)
            
    def start_param_new_amort(self, tag, amort=None):
        self.response = self._get_empty_response()
        self.response['tag'] = tag

        if tag == 'change' and amort:
            self._fill_dict_change_amort(amort)

    def _fill_dict_change_amort(self, amort):
        self.lineEdit_name.setText(f'{amort.name}')
        self.le_length_min.setText(f'{amort.min_length}')
        self.le_length_max.setText(f'{amort.max_length}')
        self.le_hod.setText(f'{amort.hod}')
        self.le_speed_one.setText(f'{amort.speed_one}')
        self.le_speed_two.setText(f'{amort.speed_two}')
        self.le_recoil_min.setText(f'{amort.min_recoil}')
        self.le_recoil_min_two.setText(f'{amort.min_recoil_2}')
        self.le_recoil_max.setText(f'{amort.max_recoil}')
        self.le_recoil_max_two.setText(f'{amort.max_recoil_2}')
        self.le_comp_min.setText(f'{amort.min_comp}')
        self.le_comp_min_two.setText(f'{amort.min_comp_2}')
        self.le_comp_max.setText(f'{amort.max_comp}')
        self.le_comp_max_two.setText(f'{amort.max_comp_2}')
        self.le_temper.setText(f'{amort.max_temper}')

        self.adapter_cb.setCurrentText(f'{amort.adapter}')
        
    def _validate_float(self, widget, key, min_val, max_val, field_name):
        try:
            text = widget.text()

            if not text:
                QMessageBox.information(self, 'Внимание', f'Заполните поле -> {field_name}')
                self.response[key] = ''
                return

            try:
                value = float(text.replace(',', '.'))
            except ValueError:
                QMessageBox.information(self, 'Внимание',
                                        f'Некорректное значение в поле -> {field_name}')
                self.response[key] = ''
                return

            if not (min_val <= value <= max_val):
                QMessageBox.information(self, 'Внимание',
                                        f'{field_name} -> ({value}) вне диапазона')
                self.response[key] = ''
                return

            self.response[key] = value
            
        except Exception as e:
            self.logger.error(e)
            
    def _validate_int(self, widget, key, min_val, max_val, field_name):
        try:
            text = widget.text().strip()

            if not text:
                QMessageBox.information(self, 'Внимание', f'Заполните поле -> {field_name}')
                self.response[key] = ''
                return

            try:
                value_f = float(text.replace(',', '.'))
            except ValueError:
                QMessageBox.information(self, 'Внимание',
                                        f'Некорректное значение в поле -> {field_name}')
                self.response[key] = ''
                return

            if not value_f.is_integer():
                QMessageBox.information(self, 'Внимание',
                                        f'Поле "{field_name}" должно быть целым числом')
                self.response[key] = ''
                return

            value = int(value_f)

            if not (min_val <= value <= max_val):
                QMessageBox.information(self, 'Внимание',
                                        f'{field_name} -> ({value}) вне диапазона')
                self.response[key] = ''
                return

            self.response[key] = value

        except Exception as e:
            self.logger.error(e)

    def _name_editing_finished(self):
        text = self.lineEdit_name.text()
        if not text:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          'Заполните поле названия амортизатора'
                                          )
            self.response['name'] = ''

        else:
            self.response['name'] = text
            
    def _len_min_editing_finished(self):
        self._validate_float(
            self.le_length_min,
            'min_length',
            100,
            1000,
            'Длина в сжатом состоянии'
        )

    def _len_max_editing_finished(self):
        self._validate_float(
            self.le_length_max,
            'max_length',
            100,
            1000,
            'Длина в разжатом состоянии'
        )

    def _hod_editing_finished(self):
        self._validate_int(
            self.le_hod,
            'hod',
            40,
            120,
            'Испытательный ход'
        )

    def _one_speed_editing_finished(self):
        hod = self.response.get('hod') or 40
        max_speed = self.calc_data.max_speed(hod)
        self._validate_float(
            self.le_speed_one,
            'speed_one',
            0.02,
            max_speed,
            'Первая скорость испытания'
        )
        
    def _two_speed_editing_finished(self):
        hod = self.response.get('hod') or 40
        max_speed = self.calc_data.max_speed(hod)
        self._validate_float(
            self.le_speed_two,
            'speed_two',
            0.02,
            max_speed,
            'Вторая скорость испытания'
        )

    def _comp_min_editing_finished(self):
        self._validate_float(
            self.le_comp_min,
            'min_comp',
            0,
            2000,
            'Минимальное усилие сжатия'
        )
        
    def _two_comp_min_editing_finished(self):
        self._validate_float(
            self.le_comp_min_two,
            'min_comp_2',
            0,
            2000,
            'Минимальное усилие сжатия второй скорости'
        )
        
    def _comp_max_editing_finished(self):
        self._validate_float(
            self.le_comp_max,
            'max_comp',
            0,
            2000,
            'Максимальное усилие сжатия'
        )
        
    def _two_comp_max_editing_finished(self):
        self._validate_float(
            self.le_comp_max_two,
            'max_comp_2',
            0,
            2000,
            'Максимальное усилие сжатия второй скорости'
        )

    def _recoil_min_editing_finished(self):
        self._validate_float(
            self.le_recoil_min,
            'min_recoil',
            0,
            2000,
            'Минимальное усилие отбоя'
        )
        
    def _two_recoil_min_editing_finished(self):
        self._validate_float(
            self.le_recoil_min_two,
            'min_recoil_2',
            0,
            2000,
            'Минимальное усилие отбоя второй скорости'
        )
        
    def _recoil_max_editing_finished(self):
        self._validate_float(
            self.le_recoil_max,
            'max_recoil',
            0,
            2000,
            'Максимальное усилие отбоя'
        )

    def _two_recoil_max_editing_finished(self):
        self._validate_float(
            self.le_recoil_max_two,
            'max_recoil_2',
            0,
            2000,
            'Максимальное усилие отбоя второй скорости'
        )
        
    def _temper_editing_finished(self):
        self._validate_float(
            self.le_temper,
            'max_temper',
            0,
            120,
            'Максимальная температура'
        )
        
    def _convert_adapter(self, name: str):
        """Перевод номера адаптера в его длинну"""
        mapping = {
            '069': 25,
            '069-01': 25,
            '069-02': 34,
            '069-03': 34,
            '069-04': 34,
            '072': 41
        }
        return mapping.get(name, 0)

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _read_data_from_gui(self):
        try:
            self._name_editing_finished()
            self._len_min_editing_finished()
            self._len_max_editing_finished()
            self._hod_editing_finished()
            self._one_speed_editing_finished()
            self._two_speed_editing_finished()
            self._comp_min_editing_finished()
            self._two_comp_min_editing_finished()
            self._comp_max_editing_finished()
            self._two_comp_max_editing_finished()
            self._recoil_min_editing_finished()
            self._two_recoil_min_editing_finished()
            self._recoil_max_editing_finished()
            self._two_recoil_max_editing_finished()
            self._temper_editing_finished()

        except Exception as e:
            self.logger.error(e)

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
            self.response['adapter'] = self.adapter_cb.currentText()
            self.response['adapter_len'] = self._convert_adapter(
                self.adapter_cb.currentText()
            )
            
            if any(value == '' for value in self.response.values()):
                return

            self._clear_data_on_gui()
            self.signals.save_amort.emit(self.response)

        except Exception as e:
            self.logger.error(e)
