# -*- coding: utf-8 -*-
import configparser

from logger import my_logger


class StructAmort(object):
    def __init__(self):
        self.amorts = []


class DataAmort(object):
    def __init__(self):
        self.name = ''
        self.min_length = 0
        self.max_length = 0
        self.hod = 0
        self.adapter = ''
        self.adapter_len = 0
        self.speed_one = 0
        self.speed_two = 0
        self.min_comp = 0
        self.min_comp_2 = 0
        self.max_comp = 0
        self.max_comp_2 = 0
        self.min_recoil = 0
        self.min_recoil_2 = 0
        self.max_recoil = 0
        self.max_recoil_2 = 0
        self.max_temper = 0


class Amort:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.names = []
        self.current_index = -1
        self.struct = StructAmort()
        self.config = configparser.ConfigParser()

    def _convert_adapter(self, name: str):
        """Перевод номера адаптера в его длинну"""
        try:
            if name == '069' or name == '069-01':
                return 25

            elif name == '069-02' or name == '069-03' or name == '069-04':
                return 34

            elif name == '072':
                return 41

            else:
                return 0

        except Exception as e:
            self.logger.error(e)

    def update_amort_list(self):
        try:
            self.names = []
            self.struct.amorts.clear()
            self.config.read("amorts.ini", encoding='utf-8')
            ind = -1
            for section in self.config.sections():
                try:
                    ind += 1
                    self.struct.amorts.append(DataAmort())
                    for key in self.config[section]:
                        temp_val = self.config.get(section, key)
                        if key == 'name':
                            self.struct.amorts[ind].name = temp_val
                            self.names.append(temp_val)
                        if key == 'hod':
                            self.struct.amorts[ind].hod = int(temp_val)
                        if key == 'adapter':
                            self.struct.amorts[ind].adapter = temp_val
                            self.struct.amorts[ind].adapter_len = self._convert_adapter(temp_val)
                        if key == 'speed_one':
                            self.struct.amorts[ind].speed_one = float(temp_val)
                        if key == 'speed_two':
                            self.struct.amorts[ind].speed_two = float(temp_val)
                        if key == 'min_length':
                            self.struct.amorts[ind].min_length = float(temp_val)
                        if key == 'max_length':
                            self.struct.amorts[ind].max_length = float(temp_val)
                        if key == 'min_comp':
                            self.struct.amorts[ind].min_comp = float(temp_val)
                        if key == 'min_comp_2':
                            self.struct.amorts[ind].min_comp_2 = float(temp_val)
                        if key == 'max_comp':
                            self.struct.amorts[ind].max_comp = float(temp_val)
                        if key == 'max_comp_2':
                            self.struct.amorts[ind].max_comp_2 = float(temp_val)
                        if key == 'min_recoil':
                            self.struct.amorts[ind].min_recoil = float(temp_val)
                        if key == 'min_recoil_2':
                            self.struct.amorts[ind].min_recoil_2 = float(temp_val)
                        if key == 'max_recoil':
                            self.struct.amorts[ind].max_recoil = float(temp_val)
                        if key == 'max_recoil_2':
                            self.struct.amorts[ind].max_recoil_2 = float(temp_val)
                        if key == 'max_temper':
                            self.struct.amorts[ind].max_temper = float(temp_val)

                except Exception as e:
                    self.logger.error(e)

        except Exception as e:
            self.logger.error(e)

    def delete_amort(self, index_del):
        try:
            self.struct.amorts.pop(index_del)
            self._write_struct_in_file()

        except Exception as e:
            self.logger.error(e)

    def add_amort(self, obj):
        try:
            max_rec = len(self.struct.amorts)
            nam_section = 'Amort' + str(max_rec)
            self.config.add_section(nam_section)

            self.config.set(nam_section, 'name', obj.get('name'))
            self.config.set(nam_section, 'hod', obj.get('hod'))
            self.config.set(nam_section, 'adapter', obj.get('adapter'))
            self.config.set(nam_section, 'speed_one', obj.get('speed_one'))
            self.config.set(nam_section, 'speed_two', obj.get('speed_two'))
            self.config.set(nam_section, 'min_length', obj.get('len_min'))
            self.config.set(nam_section, 'max_length', obj.get('len_max'))

            self.config.set(nam_section, 'min_comp', obj.get('comp_min'))
            self.config.set(nam_section, 'min_comp_2', obj.get('comp_min_2'))
            self.config.set(nam_section, 'max_comp', obj.get('comp_max'))
            self.config.set(nam_section, 'max_comp_2', obj.get('comp_max_2'))

            self.config.set(nam_section, 'min_recoil', obj.get('recoil_min'))
            self.config.set(nam_section, 'min_recoil_2', obj.get('recoil_min_2'))
            self.config.set(nam_section, 'max_recoil', obj.get('recoil_max'))
            self.config.set(nam_section, 'max_recoil_2', obj.get('recoil_max_2'))
            self.config.set(nam_section, 'max_temper', obj.get('temper'))

            with open('amorts.ini', 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)

        except Exception as e:
            self.logger.error(e)

    def change_amort(self, ind, obj):
        try:
            self.struct.amorts[ind].name = obj.get('name')
            self.struct.amorts[ind].min_length = obj.get('len_min')
            self.struct.amorts[ind].max_length = obj.get('len_max')
            self.struct.amorts[ind].hod = obj.get('hod')
            self.struct.amorts[ind].adapter = obj.get('adapter')
            self.struct.amorts[ind].speed_one = obj.get('speed_one')
            self.struct.amorts[ind].speed_two = obj.get('speed_two')
            self.struct.amorts[ind].min_comp = obj.get('comp_min')
            self.struct.amorts[ind].min_comp_2 = obj.get('comp_min_2')
            self.struct.amorts[ind].max_comp = obj.get('comp_max')
            self.struct.amorts[ind].max_comp_2 = obj.get('comp_max_2')
            self.struct.amorts[ind].min_recoil = obj.get('recoil_min')
            self.struct.amorts[ind].min_recoil_2 = obj.get('recoil_min_2')
            self.struct.amorts[ind].max_recoil = obj.get('recoil_max')
            self.struct.amorts[ind].max_recoil_2 = obj.get('recoil_max_2')
            self.struct.amorts[ind].max_temper = obj.get('temper')

            self._write_struct_in_file()

        except Exception as e:
            self.logger.error(e)

    def _write_struct_in_file(self):
        try:
            self.config.clear()

            for i in range(len(self.struct.amorts)):
                nam_section = 'Amort' + str(i)
                self.config.add_section(nam_section)

                self.config.set(nam_section, 'name', self.struct.amorts[i].name)
                self.config.set(nam_section, 'hod', str(self.struct.amorts[i].hod))
                self.config.set(nam_section, 'adapter', str(self.struct.amorts[i].adapter))
                self.config.set(nam_section, 'speed_one', str(self.struct.amorts[i].speed_one))
                self.config.set(nam_section, 'speed_two', str(self.struct.amorts[i].speed_two))
                self.config.set(nam_section, 'min_length', str(self.struct.amorts[i].min_length))
                self.config.set(nam_section, 'max_length', str(self.struct.amorts[i].max_length))

                self.config.set(nam_section, 'min_comp', str(self.struct.amorts[i].min_comp))
                self.config.set(nam_section, 'min_comp_2', str(self.struct.amorts[i].min_comp_2))
                self.config.set(nam_section, 'max_comp', str(self.struct.amorts[i].max_comp))
                self.config.set(nam_section, 'max_comp_2', str(self.struct.amorts[i].max_comp_2))

                self.config.set(nam_section, 'min_recoil', str(self.struct.amorts[i].min_recoil))
                self.config.set(nam_section, 'min_recoil_2', str(self.struct.amorts[i].min_recoil_2))
                self.config.set(nam_section, 'max_recoil', str(self.struct.amorts[i].max_recoil))
                self.config.set(nam_section, 'max_recoil_2', str(self.struct.amorts[i].max_recoil_2))
                self.config.set(nam_section, 'max_temper', str(self.struct.amorts[i].max_temper))

            with open('amorts.ini', "w", encoding='utf-8') as configfile:
                self.config.write(configfile)

        except Exception as e:
            self.logger.error(e)
