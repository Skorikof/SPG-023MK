import serial
import modbus_tk.modbus_rtu as modbus_rtu
from typing import Optional, Dict, Any

from scripts.logger import my_logger
from scripts.settings import PrgSettings


class Client:
    """Modbus RTU client wrapper with connection management"""
    DEFAULT_TIMEOUT = 0.1
    
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.settings = PrgSettings()
        self.set_dict: Dict[str, Any] = self.settings.con_set
        self.client: Optional[modbus_rtu.RtuMaster] = None
        self.flag_connect: bool = False

    def _init_connect(self) -> bool:
        """Initialize Modbus RTU client connection.
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            port_config = serial.Serial(
                port=self.set_dict.get('COM'),
                baudrate=self.set_dict.get('baudrate'),
                bytesize=self.set_dict.get('bytesize'),
                parity=self.set_dict.get('parity'),
                stopbits=self.set_dict.get('stopbits'),
                timeout=self.set_dict.get('timeout', 0.000001)
            )
            
            self.client = modbus_rtu.RtuMaster(port_config)
            self.client.set_timeout(self.DEFAULT_TIMEOUT)
            self.client.set_verbose(True)
            return True
            
        except Exception as e:
            self.client = None
            self.logger.error(f"Failed to initialize client: {e}")
            return False

    def connect_client(self) -> bool:
        """Connect to Modbus RTU device.
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.client is None:
                if not self._init_connect():
                    return False
            
            self.client.open()
            self.flag_connect = True
            self.logger.info("Client connected successfully")
            return True
            
        except Exception as e:
            self.flag_connect = False
            self.logger.error(f"Failed to connect client: {e}")
            return False

    def disconnect_client(self) -> None:
        """Disconnect from Modbus RTU device"""
        try:
            if self.client:
                self.client.close()
                self.flag_connect = False
            self.client = None
            self.logger.info("Client disconnected")
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect client: {e}")

    def is_connected(self) -> bool:
        """Check if client is connected.
        Returns:
            bool: True if connected, False otherwise
        """
        return self.flag_connect and self.client is not None
