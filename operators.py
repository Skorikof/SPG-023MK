# -*- coding: utf-8 -*-
import configparser

from logger import my_logger

class Operators:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.names = []
        self.ranks = []
        self.config = configparser.ConfigParser()
        self.current_index = -1

    def update_list(self):
        try:
            self.names = []
            self.ranks = []
            self.config.read('operators.ini')
            for section in self.config.sections():
                try:
                    for key in self.config[section]:
                        temp_val = self.config.get(section, key)
                        if key == 'name':
                            self.names.append(temp_val)
                        if key == 'rank':
                            self.ranks.append(temp_val)
                except Exception as e:
                    self.logger.error(e)

        except Exception as e:
            self.logger.error(e)

    def delete_operator(self, index):
        try:
            self.names.pop(index)
            self.ranks.pop(index)

            self.config.clear()

            for i in range(len(self.names)):
                nam_section = 'Operator' + str(i)
                self.config.add_section(nam_section)
                self.config.set(nam_section, 'name', self.names[i])
                self.config.set(nam_section, 'rank', self.ranks[i])

            with open('operators.ini', 'w', encoding='cp1251') as configfile:
                self.config.write(configfile)

        except Exception as e:
            self.logger.error(e)

    def add_operator(self, name, rank):
        try:
            max_rec = len(self.config.sections())
            name_section = 'Operator' + str(max_rec)
            self.config.add_section(name_section)
            self.config.set(name_section, 'name', name)
            self.config.set(name_section, 'rank', rank)

            with open('operators.ini', 'w', encoding='cp1251') as configfile:
                self.config.write(configfile)

        except Exception as e:
            self.logger.error(e)


