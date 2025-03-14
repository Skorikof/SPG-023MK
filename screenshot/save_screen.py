import os
from PIL import ImageGrab

from logger import my_logger


class ScreenSave:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

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

    def create_dir_for_save(self, main_dir, date_dir):
        try:
            directory = f'screens/{main_dir}/{date_dir}'
            os.makedirs(directory, exist_ok=True)

        except Exception as e:
            self.logger.error(e)

    def name_screen_for_save(self, obj):
        try:
            time = obj.time_test.replace(':', '.')
            name = (f'{time}_'
                    f'{obj.amort.name}_'
                    f'{obj.serial_number}_'
                    f'{obj.speed}')

            return name

        except Exception as e:
            self.logger.error(e)

    def name_screen_for_save_speed(self, obj):
        try:
            time = obj[0].time_test.replace(':', '.')
            name = (f'{time}_'
                    f'{obj[0].amort.name}_'
                    f'{obj[0].serial_number}_'
                    f'{obj[0].speed}~{obj[-1].speed}')

            return name

        except Exception as e:
            self.logger.error(e)

    def name_screen_for_save_temper(self, obj):
        try:
            time = obj.time_test.replace(':', '.')
            begin_temp = obj.temper_graph[0]
            finish_temp = obj.temper_graph[-1]
            name = (f'{time}_'
                    f'{obj.amort.name}_'
                    f'{obj.serial_number}_'
                    f'{begin_temp}~{finish_temp} °С')

            return name

        except Exception as e:
            self.logger.error(e)
