from pymodbus.client import ModbusSerialClient as ModbusClient

from scripts.logger import my_logger


class Client:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

        self.client = None
        self.flag_connect = False

    def _init_client(self):
        try:
            self.client = ModbusClient(port='COM4',
                                       parity='N',
                                       baudrate=460800,
                                       bytesize=8,
                                       stopbits=1,
                                       retries=1)

        except Exception as e:
            self.client = None
            self.logger.error(e)

    def connect_client(self):
        if self.client is None:
            self._init_client()

        self.client.connect()
        self.flag_connect = True

    def disconnect_client(self):
        if self.client:
            self.client.close()
            self.flag_connect = False
            self.client = None
