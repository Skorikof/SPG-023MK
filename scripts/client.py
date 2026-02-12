from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.framer import FramerType

from config import config
from scripts.logger import my_logger


class Client:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

        self.client = None
        self.flag_connect = False

    def _init_client(self):
        try:
            self.client = ModbusClient(framer=FramerType.RTU,
                                       port=config.comport,
                                       baudrate=config.baudrate,
                                       bytesize=8,
                                       parity='N',
                                       stopbits=1,
                                       # handle_local_echo=False,
                                       timeout=config.timeout,
                                       retries=config.retries,
                                       # trace_packet=self.trace_paket,
                                       )

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
            
    def trace_paket(self, *args, **kwargs):
        """Функция для анализа отправляемых посылок по modbus"""
        if args:
            print(f'Trace_paket args --> {args}')
        if kwargs:
            for k, v in kwargs.items():
                print(f'Trace_packet --> {k} - {v}')
