import crcmod

from scripts.logger import my_logger

class FreqControl:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def freq_command(self, tag, adr, speed, freq, hod):
        try:
            self.logger.debug(f'FC command: {tag=}, {adr=}, {speed=}, {freq=}, {hod=}')
            if tag == 'up':
                return self._motor_up(adr)
                
            elif tag == 'down':
                return self._motor_down(adr)
            
            elif tag == 'stop':
                return self._motor_stop(adr)
                
            elif tag == 'speed':
                return self._get_speed_motor(adr, speed, freq, hod)
                
            elif tag == 'max':
                return self._get_max_frequency(adr, freq)

        except Exception as e:
            self.logger.error(e)

    def _get_max_frequency(self, adr_freq, freq):
        try:
            freq = freq * 100
            freq_hex = hex(freq)[2:].zfill(4)
            com_hex = f'0{adr_freq}06010B{freq_hex}'
            com_crc = com_hex + self._calc_crc(com_hex)
            values = self._values_freq_command(com_crc)

            return values

        except Exception as e:
            self.logger.error(e)

    def _get_speed_motor(self, adr: int, speed: float = None, freq: int = None, hod: int = None):
        """
        Запись скорости вращения двигателя, если задана скорость, то она пересчитывается в частоту,
        частота записывается напрямую
        """
        try:
            value = 0
            if not freq:
                if not hod:
                    if self.amort is None:
                        hod = 120
                    else:
                        hod = self.amort.hod
                value = self._freq_from_speed(speed, hod)

            elif not speed:
                value = 100 * freq

            freq_hex = hex(value)[2:].zfill(4)
            com_hex = f'0{adr}06010D{freq_hex}'
            com_crc = com_hex + self._calc_crc(com_hex)
            values = self._values_freq_command(com_crc)

            return values

        except Exception as e:
            self.logger.error(e)

    def _motor_up(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000002'
            com_crc = com_hex + self._calc_crc(com_hex)
            values = self._values_freq_command(com_crc)

            return values

        except Exception as e:
            self.logger.error(e)

    def _motor_down(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000001'
            com_crc = com_hex + self._calc_crc(com_hex)
            values = self._values_freq_command(com_crc)

            return values

        except Exception as e:
            self.logger.error(e)

    def _motor_stop(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000003'
            com_crc = com_hex + self._calc_crc(com_hex)
            values = self._values_freq_command(com_crc)

            return values

        except Exception as e:
            self.logger.error(e)

    def _calc_crc(self, data):
        try:
            byte_data = bytes.fromhex(data)
            crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
            crc_str = hex(crc16(byte_data))[2:].zfill(4)
            crc_str = crc_str[2:] + crc_str[:2]

            return crc_str

        except Exception as e:
            self.logger.error(e)

    def _values_freq_command(self, data):
        try:
            val_regs = []
            for i in range(0, len(data), 4):
                temp = data[i:i + 4]
                temp_byte = bytearray.fromhex(temp)
                temp_val = int.from_bytes(temp_byte, 'big')
                val_regs.append(temp_val)

            return val_regs

        except Exception as e:
            self.logger.error(e)
            
    def _freq_from_speed(self, speed: float, hod: int):
        """Пересчёт скорости в частоту для записи в частотник"""
        try:
            koef = round((2 * 17.99) / (2 * 3.1415 * 0.98), 5)
            hod = hod / 1000
            radius = hod / 2
            freq = int(100 * (koef * speed) / radius)

            return freq

        except Exception as e:
            self.logger.error(e)
