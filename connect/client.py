import serial
import modbus_tk.modbus_rtu as modbus_rtu

from logger import my_logger
from settings.settings import PrgSettings


class Client:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.set_dict = PrgSettings().con_set

        self.client = None

    def _init_connect(self):
        try:
            self.client = modbus_rtu.RtuMaster(serial.Serial(port=self.set_dict.get('COM'),
                                                             baudrate=self.set_dict.get('baudrate'),
                                                             bytesize=self.set_dict.get('bytesize'),
                                                             parity=self.set_dict.get('parity'),
                                                             stopbits=self.set_dict.get('stopbits'),
                                                             timeout=0.000001))

            self.client.set_timeout(1.0)
            self.client.set_verbose(True)

        except Exception as e:
            self.client = None
            self.logger.error(e)

    def connect_client(self):
        if self.client is None:
            self._init_connect()

        self.client.open()
        self.set_dict['connect'] = True

    def disconnect_client(self):
        if self.client:
            self.client.close()
            self.set_dict['connect'] = False
            self.client = None
