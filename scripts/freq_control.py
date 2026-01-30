import crcmod
from enum import Enum

from scripts.logger import my_logger


class MotorCommand(Enum):
    """Команды управления двигателем"""
    UP = '0620000002'
    DOWN = '0620000001'
    STOP = '0620000003'


class FreqControl:
    # Константы для команд
    COMMAND_MAX_FREQ = '06010B'
    COMMAND_SPEED = '06010D'
    
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def freq_command(self, tag, adr, speed=None, freq=None, hod=None):
        """
        Главный метод для отправки команд частотнику
        Args:
            tag: тип команды ('up', 'down', 'stop', 'speed', 'max')
            adr: адрес устройства
            speed: скорость (м/с)
            freq: частота (Гц)
            hod: ход поршня (мм)
            
        Returns:
            tuple: (значения регистров, тег команды)
        """
        try:
            self.logger.debug(f'FC command: {tag=}, {adr=}, {speed=}, {freq=}, {hod=}')
            
            command_map = {
                'up': lambda: self._motor_command(adr, MotorCommand.UP),
                'down': lambda: self._motor_command(adr, MotorCommand.DOWN),
                'stop': lambda: self._motor_command(adr, MotorCommand.STOP),
                'speed': lambda: self._get_speed_motor(adr, speed, freq, hod),
                'max': lambda: self._get_max_frequency(adr, freq),
            }
            
            if tag not in command_map:
                self.logger.error(f'Неизвестная команда для частотника: {tag}')
                return None, tag
                
            result = command_map[tag]()
            return result, tag

        except Exception as e:
            self.logger.error(f'Ошибка в freq_command: {e}')
            raise

    def _motor_command(self, adr: int, command: MotorCommand):
        """Универсальный метод для команд управления двигателем"""
        try:
            com_hex = f'0{adr}{command.value}'
            com_crc = com_hex + self._calc_crc(com_hex)
            return self._values_freq_command(com_crc)
        except Exception as e:
            self.logger.error(f'Ошибка в _motor_command: {e}')
            raise

    def _get_max_frequency(self, adr: int, freq: int):
        """Установка максимальной частоты"""
        try:
            if not isinstance(freq, (int, float)) or freq <= 0:
                raise ValueError(f'Некорректная частота: {freq}')
                
            freq = int(freq * 100)
            freq_hex = hex(freq)[2:].zfill(4)
            com_hex = f'0{adr}{self.COMMAND_MAX_FREQ}{freq_hex}'
            com_crc = com_hex + self._calc_crc(com_hex)
            return self._values_freq_command(com_crc)

        except Exception as e:
            self.logger.error(f'Ошибка в _get_max_frequency: {e}')
            raise

    def _get_speed_motor(self, adr: int, speed: float = None, freq: int = None, hod: int = None):
        """
        Запись скорости вращения двигателя.
        Если задана скорость, то она пересчитывается в частоту.
        Если задана частота, то она записывается напрямую.
        """
        try:
            if freq is not None:
                value = int(100 * freq)
            elif speed is not None:
                if hod is None:
                    raise ValueError('Для расчета скорости требуется параметр hod')
                value = self._freq_from_speed(speed, hod)
            else:
                raise ValueError('Должны быть заданы speed или freq')

            freq_hex = hex(value)[2:].zfill(4)
            com_hex = f'0{adr}{self.COMMAND_SPEED}{freq_hex}'
            com_crc = com_hex + self._calc_crc(com_hex)
            return self._values_freq_command(com_crc)

        except Exception as e:
            self.logger.error(f'Ошибка в _get_speed_motor: {e}')
            raise

    def _calc_crc(self, data: str) -> str:
        """Расчет CRC16"""
        try:
            byte_data = bytes.fromhex(data)
            crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
            crc_str = hex(crc16(byte_data))[2:].zfill(4)
            return crc_str[2:] + crc_str[:2]

        except Exception as e:
            self.logger.error(f'Ошибка в _calc_crc: {e}')
            raise

    def _values_freq_command(self, data: str) -> list:
        """Преобразование hex-строки в список значений регистров"""
        try:
            val_regs = []
            for i in range(0, len(data), 4):
                temp = data[i:i + 4]
                temp_byte = bytearray.fromhex(temp)
                temp_val = int.from_bytes(temp_byte, 'big')
                val_regs.append(temp_val)
            return val_regs

        except Exception as e:
            self.logger.error(f'Ошибка в _values_freq_command: {e}')
            raise
            
    def _freq_from_speed(self, speed: float, hod: int) -> int:
        """Пересчёт скорости в частоту для записи в частотник"""
        try:
            if not isinstance(speed, (int, float)) or speed < 0:
                raise ValueError(f'Некорректная скорость: {speed}')
            if not isinstance(hod, (int, float)) or hod <= 0:
                raise ValueError(f'Некорректный ход: {hod}')
                
            koef = round((2 * 17.99) / (2 * 3.1415 * 0.98), 5)
            hod_m = hod / 1000
            radius = hod_m / 2
            freq = int(100 * (koef * speed) / radius)
            return freq

        except Exception as e:
            self.logger.error(f'Ошибка в _freq_from_speed: {e}')
            raise
