import configparser


class StructDampers(object):
    def __init__(self):
        self.dampers = []


class DataDampers(object):
    def __init__(self):
        self.name_d = ''
        self.min_length = 0
        self.max_length = 0
        self.bracket_height = 0
        self.speed = 0
        self.angle = 0
        self.min_comp = 0
        self.max_comp = 0
        self.min_recoil = 0
        self.max_recoil = 0
        self.max_temper = 0
        self.beta = 0


class Damper:
    def __init__(self):
        result = dict()
        self.struct = StructDampers()
        self.config = configparser.ConfigParser()

    def update_damper_list(self):
        try:
            self.struct.dampers.clear()
            self.config.read("dampers.ini")
            index_d=-1
            for section in self.config.sections():
                try:
                    index_d+=1
                    self.struct.dampers.append(DataDampers())
                    for key in self.config[section]:
                        temp_val=self.config.get(section,key)
                        if key=='name':
                            self.struct.dampers[index_d].name_d=temp_val
                        if key=='min_length':
                            self.struct.dampers[index_d].min_length=int(temp_val)
                        if key=='max_length':
                            self.struct.dampers[index_d].max_length=int(temp_val)
                        if key=='bracket_height':
                            self.struct.dampers[index_d].bracket_height =int(temp_val)
                        if key=='speed':
                            self.struct.dampers[index_d].speed =float(temp_val)
                        if key=='angle':
                            self.struct.dampers[index_d].angle=int(temp_val)
                        if key=='min_comp':
                            self.struct.dampers[index_d].min_comp=int(temp_val)
                        if key=='max_comp':
                            self.struct.dampers[index_d].max_comp=int(temp_val)
                        if key=='min_recoil':
                            self.struct.dampers[index_d].min_recoil=int(temp_val)
                        if key=='max_recoil':
                            self.struct.dampers[index_d].max_recoil=int(temp_val)
                        if key=='max_temper':
                            self.struct.dampers[index_d].max_temper=int(temp_val)

                except Exception as e:
                    print(str(e))

        except Exception as e:
            print(str(e))

    def delete_damper(self, index_del):
        try:
            txt_temp = 'name = {}, min_length = {}, max_length = {}, bracket_height = {},speed = {},' \
                     'angle = {},min_compression = {},max_compression = {}, min_recoil = {}, ' \
                     'max_recoil = {}, max_temper = {}'.format( self.struct.dampers[index_del].name_d, \
                     self.struct.dampers[index_del].min_length, self.struct.dampers[index_del].max_length, \
                     self.struct.dampers[index_del].bracket_height, self.struct.dampers[index_del].speed, \
                     self.struct.dampers[index_del].angle, self.struct.dampers[index_del].min_comp, \
                    self.struct.dampers[index_del].max_comp, self.struct.dampers[index_del].min_recoil, \
                    self.struct.dampers[index_del].max_recoil, self.struct.dampers[index_del].max_temper)
            self.logger.info('DAMPER is deleted: ' + txt_temp)
            self.struct.dampers.pop(index_del)
            self.config.clear()

            for i in range(len(self.struct.dampers)):
                nam_section='Damper' + str(i)
                self.config.add_section(nam_section)

                self.config.set(nam_section,'name',self.struct.dampers[i].name_d)
                self.config.set(nam_section,'min_length',str(self.struct.dampers[i].min_length))
                self.config.set(nam_section,'max_length',str(self.struct.dampers[i].max_length))
                self.config.set(nam_section,'bracket_height',str(self.struct.dampers[i].bracket_height))

                self.config.set(nam_section,'speed',str(self.struct.dampers[i].speed))
                self.config.set(nam_section,'angle',str(self.struct.dampers[i].angle))
                self.config.set(nam_section,'min_comp',str(self.struct.dampers[i].min_comp))
                self.config.set(nam_section,'max_comp',str(self.struct.dampers[i].max_comp))

                self.config.set(nam_section,'min_recoil',str(self.struct.dampers[i].min_recoil))
                self.config.set(nam_section,'max_recoil',str(self.struct.dampers[i].max_recoil))
                self.config.set(nam_section,'max_temper',str(self.struct.dampers[i].max_temper))

            with open('Dampers.ini', "w") as configfile:
                self.config.write(configfile)
        except Exception as e:
            self.logger.error(e)
            #print('Ошибки в файле Dampers.ini {}'.format(e))

    #добавление нового гасителя в список
    def add_damper(self, obj):
        try:
            max_rec=len(self.struct.dampers)
            #self.config.read("OperatorsList.ini")  # читаем конфиг
            nam_section='Damper' + str(max_rec)
            self.config.add_section(nam_section)

            self.config.set(nam_section,'name',obj.name_d)
            self.config.set(nam_section,'min_length',str(obj.min_length))
            self.config.set(nam_section,'max_length',str(obj.max_length))
            self.config.set(nam_section,'bracket_height',str(obj.bracket_height))

            self.config.set(nam_section,'speed',str(obj.speed))
            self.config.set(nam_section,'angle',str(obj.angle))
            self.config.set(nam_section,'min_comp',str(obj.min_comp))
            self.config.set(nam_section,'max_comp',str(obj.max_comp))

            self.config.set(nam_section,'min_recoil',str(obj.min_recoil))
            self.config.set(nam_section,'max_recoil',str(obj.max_recoil))
            self.config.set(nam_section,'max_temper',str(obj.max_temper))
            with open('Dampers.ini', 'w') as configfile:
                self.config.write(configfile)

            #запись в лог добавленного гасителя
            txt_temp='name = {}, min_length = {}, max_length = {}, bracket_height = {},speed = {},' \
                     'angle = {},min_compression = {},max_compression = {}, min_recoil = {}, ' \
                     'max_recoil = {}, max_temper = {}'.format(
                obj.name_d, obj.min_length, obj.max_length, obj.bracket_height, obj.speed, obj.angle,
                obj.min_comp, obj.max_comp, obj.min_recoil, obj.max_recoil, obj.max_temper)

            self.logger.info('DAMPER is added: ' + txt_temp)

        except Exception as e:
            self.logger.error(e)
            #print('Ошибки в файле Dampers.ini {}'.format(e))
