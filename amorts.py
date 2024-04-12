import configparser


class StructAmort(object):
    def __init__(self):
        self.amorts = []


class DataAmort(object):
    def __init__(self):
        self.name_a = ''
        self.min_length = 0
        self.max_length = 0
        self.min_comp = 0
        self.max_comp = 0
        self.min_recoil = 0
        self.max_recoil = 0
        self.max_temper = 0
        self.speed = 0
        self.beta = 0


class Amort:
    def __init__(self):
        self.names = []
        self.current_index = -1
        self.struct = StructAmort()
        self.config = configparser.ConfigParser()

    def update_amort_list(self):
        try:
            self.names = []
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
                            self.struct.amorts[index_d].name_a = temp_val
                            self.names.append(temp_val)
                        if key == 'min_length':
                            self.struct.amorts[index_d].min_length = int(temp_val)
                        if key == 'max_length':
                            self.struct.amorts[index_d].max_length = int(temp_val)
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
                        if key == 'speed':
                            self.struct.amorts[index_d].speed = float(temp_val)

                except Exception as e:
                    print(str(e))

        except Exception as e:
            print(str(e))

    def delete_amort(self, index_del):
        try:
            self.struct.amorts.pop(index_del)
            self.config.clear()

            for i in range(len(self.struct.amorts)):
                nam_section = 'Amort' + str(i)
                self.config.add_section(nam_section)

                self.config.set(nam_section, 'name', self.struct.amorts[i].name_a)
                self.config.set(nam_section, 'min_length', str(self.struct.amorts[i].min_length))
                self.config.set(nam_section, 'max_length', str(self.struct.amorts[i].max_length))

                self.config.set(nam_section, 'min_comp', str(self.struct.amorts[i].min_comp))
                self.config.set(nam_section, 'max_comp', str(self.struct.amorts[i].max_comp))

                self.config.set(nam_section, 'min_recoil', str(self.struct.amorts[i].min_recoil))
                self.config.set(nam_section, 'max_recoil', str(self.struct.amorts[i].max_recoil))
                self.config.set(nam_section, 'max_temper', str(self.struct.amorts[i].max_temper))
                self.config.set(nam_section, 'speed', str(self.struct.amorts[i].speed))

            with open('amorts.ini', "w") as configfile:
                self.config.write(configfile)

        except Exception as e:
            print('Ошибки в файле amorts.ini {}'.format(e))

    def add_amort(self, obj):
        try:
            max_rec = len(self.struct.amorts)
            nam_section = 'Amort' + str(max_rec)
            self.config.add_section(nam_section)

            self.config.set(nam_section, 'name', obj.get('name'))
            self.config.set(nam_section, 'min_length', obj.get('len_min'))
            self.config.set(nam_section, 'max_length', obj.get('len_max'))

            self.config.set(nam_section, 'min_comp', obj.get('comp_min'))
            self.config.set(nam_section, 'max_comp', obj.get('comp_max'))

            self.config.set(nam_section, 'min_recoil', obj.get('recoil_min'))
            self.config.set(nam_section, 'max_recoil', obj.get('recoil_max'))
            self.config.set(nam_section, 'max_temper', obj.get('max_temper'))
            self.config.set(nam_section, 'speed', obj.get('speed'))

            with open('amorts.ini', 'w') as configfile:
                self.config.write(configfile)

        except Exception as e:
            print('Ошибки в файле amorts.ini {}'.format(e))
