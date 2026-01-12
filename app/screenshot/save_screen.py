import os
from PIL import ImageGrab

from scripts.logger import my_logger


class ScreenSave:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def select_type_test(self, type_graph):
        try:
            if type_graph == 'move':
                return 'Усилие_Перемещение'    
            elif type_graph == 'boost_1':
                return 'Скорость_Сопротивление №1'
            elif type_graph == 'boost_2':
                return 'Скорость_Сопротивление №2'
            elif type_graph == 'triple':
                return 'Ход_Скорость_Сопротивление'
            elif type_graph == 'speed':
                return 'Усилие_Скорость'
            elif type_graph == 'temper':
                return 'Температура_Сопротвление'
            
        except Exception as e:
            self.logger.error(e)
            
    def name_for_screenshot(self, type_test, arch_obj):
        try:
            time = arch_obj.time_test.replace(':', '.')
            first = (f'{time}_'
                     f'{arch_obj.name}_'
                     f'{arch_obj.serial_number}_')
            
            if type_test == 'casc':
                second = f'{arch_obj.speed_list[0]}~{arch_obj.speed_list[-1]}'
            
            elif type_test == 'temper':
                second = f'{arch_obj.temper_list[0]}~{arch_obj.temper_list[-1]} °С'
            else:
                second = f'{arch_obj.speed}'    

            full = first + second
            
            return full
            
        except Exception as e:
            self.logger.error(e)
            
    def create_dir_for_save(self, main_dir, type_graph, date_dir):
        try:
            directory = f'screens/{main_dir}/{type_graph}/{date_dir}'
            os.makedirs(directory, exist_ok=True)

        except Exception as e:
            self.logger.error(e)

    def create_image_for_save(self, frame_geometry):
        try:
            pos = frame_geometry.getRect()
            x = pos[0] + 1
            y = pos[1] + 80
            height = 820
            width = 1024

            return ImageGrab.grab((x, y, x + width, y + height))

        except Exception as e:
            self.logger.error(e)
