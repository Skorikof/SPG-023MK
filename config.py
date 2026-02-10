import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
    
    @property
    def comport(self) -> str:
        return os.getenv("COM", "COM1")
    
    @property
    def baudrate(self) -> int:
        return int(os.getenv("BAUDRATE", "460800"))
    
    @property
    def force_koef(self) -> float:
        return float(os.getenv("FORCE_KOEF", "1"))
    
    @property
    def finish_temper(self) -> int:
        return int(os.getenv("FINISH_TEMPER", "80"))
    
    @property
    def log_level(self) -> int:
        return int(os.getenv("LOG_LEVEL", "20"))
    
config = Config()
