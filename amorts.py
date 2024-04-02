import configparser


class StructAmort(object):
    def __init__(self):
        self.amorts = []


class DataAmort(object):
    def __init__(self):
        self.name_d = ''
        self.min_length = 0
        self.max_length = 0
        self.speed = 0
        self.min_comp = 0
        self.max_comp = 0
        self.min_recoil = 0
        self.max_recoil = 0
        self.max_temper = 0
        self.beta = 0


class Amort:
    def __init__(self):
        self.struct = StructAmort()
        self.config = configparser.ConfigParser()

    def update_amort_list(self):
        try:
            self.struct.amorts.clear()
            self.config.read("amorts.ini")
            index_d = -1
            for section in self.config.sections():
                try:
                    index_d += 1
                    self.struct.amorts.append(DataAmort())
                    for key in self.config[section]:
                        temp_val = self.config.get(section, key)
                        if key == 'name':
                            self.struct.amorts[index_d].name_d = temp_val
                        if key == 'min_length':
                            self.struct.amorts[index_d].min_length = int(temp_val)
                        if key == 'max_length':
                            self.struct.amorts[index_d].max_length = int(temp_val)
                        if key == 'speed':
                            self.struct.amorts[index_d].speed = float(temp_val)
                        if key == 'min_comp':
                            self.struct.amorts[index_d].min_comp = int(temp_val)
                        if key == 'max_comp':
                            self.struct.amorts[index_d].max_comp = int(temp_val)
                        if key == 'min_recoil':
                            self.struct.amorts[index_d].min_recoil = int(temp_val)
                        if key == 'max_recoil':
                            self.struct.amorts[index_d].max_recoil = int(temp_val)
                        if key == 'max_temper':
                            self.struct.amorts[index_d].max_temper = int(temp_val)

                except Exception as e:
                    print(str(e))

        except Exception as e:
            print(str(e))

    def delete_amort(self, index_del):
        try:
            # txt_temp = 'name = {}, min_length = {},' \
            #            'max_length = {},speed = {},' \
            #            'min_compression = {}, max_compression = {},' \
            #            'min_recoil = {}, max_recoil = {},' \
            #            'max_temper = {}'.format(self.struct.dampers[index_del].name_d,
            #                                     self.struct.dampers[index_del].min_length,
            #                                     self.struct.dampers[index_del].max_length,
            #                                     self.struct.dampers[index_del].speed,
            #                                     self.struct.dampers[index_del].min_comp,
            #                                     self.struct.dampers[index_del].max_comp,
            #                                     self.struct.dampers[index_del].min_recoil,
            #                                     self.struct.dampers[index_del].max_recoil,
            #                                     self.struct.dampers[index_del].max_temper)
            # self.logger.info('DAMPER is deleted: ' + txt_temp)
            self.struct.amorts.pop(index_del)
            self.config.clear()

            for i in range(len(self.struct.amorts)):
                nam_section = 'Amort' + str(i)
                self.config.add_section(nam_section)

                self.config.set(nam_section, 'name', self.struct.amorts[i].name_d)
                self.config.set(nam_section, 'min_length', str(self.struct.amorts[i].min_length))
                self.config.set(nam_section, 'max_length', str(self.struct.amorts[i].max_length))

                self.config.set(nam_section, 'speed', str(self.struct.amorts[i].speed))
                self.config.set(nam_section, 'min_comp', str(self.struct.amorts[i].min_comp))
                self.config.set(nam_section, 'max_comp', str(self.struct.amorts[i].max_comp))

                self.config.set(nam_section, 'min_recoil', str(self.struct.amorts[i].min_recoil))
                self.config.set(nam_section, 'max_recoil', str(self.struct.amorts[i].max_recoil))
                self.config.set(nam_section, 'max_temper', str(self.struct.amorts[i].max_temper))

            with open('amorts.ini', "w") as configfile:
                self.config.write(configfile)

        except Exception as e:
            # self.logger.error(e)
            print('Ошибки в файле amorts.ini {}'.format(e))

    def add_amort(self, obj):
        try:
            max_rec = len(self.struct.amorts)
            nam_section = 'Amort' + str(max_rec)
            self.config.add_section(nam_section)

            self.config.set(nam_section, 'name', obj.name_d)
            self.config.set(nam_section, 'min_length', str(obj.min_length))
            self.config.set(nam_section, 'max_length', str(obj.max_length))

            self.config.set(nam_section, 'speed', str(obj.speed))
            self.config.set(nam_section, 'min_comp', str(obj.min_comp))
            self.config.set(nam_section, 'max_comp', str(obj.max_comp))

            self.config.set(nam_section, 'min_recoil', str(obj.min_recoil))
            self.config.set(nam_section, 'max_recoil', str(obj.max_recoil))
            self.config.set(nam_section, 'max_temper', str(obj.max_temper))
            with open('amorts.ini', 'w') as configfile:
                self.config.write(configfile)

            # txt_temp = 'name = {}, min_length = {},' \
            #            'max_length = {}, speed = {},' \
            #            'min_compression = {},max_compression = {},' \
            #            'min_recoil = {}, max_recoil = {},' \
            #            'max_temper = {}'.format(obj.name_d, obj.min_length,
            #                                     obj.max_length, obj.speed,
            #                                     obj.min_comp, obj.max_comp,
            #                                     obj.min_recoil, obj.max_recoil,
            #                                     obj.max_temper)
            #
            # self.logger.info('DAMPER is added: ' + txt_temp)

        except Exception as e:
            # self.logger.error(e)
            print('Ошибки в файле amorts.ini {}'.format(e))
