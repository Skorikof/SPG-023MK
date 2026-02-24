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
    def timeout(self) -> float:
        return float(os.getenv("TIMEOUT", "0.02"))
    
    @property
    def retries(self) -> int:
        return int(os.getenv("RETRIES", "1"))

    @property
    def pause_reg(self) -> float:
        return float(os.getenv("PAUSE_REG", "0.05"))
    
    @property
    def pause_buf(self) -> float:
        return float(os.getenv("PAUSE_BUF", "0.01"))
    
    @property
    def pause_write(self) -> float:
        return float(os.getenv("PAUSE_WRITE", "0.005"))
    
    @property
    def const_traverse(self) -> int:
        return int(os.getenv("CONST_TRAV", "760"))
    
    @property
    def freq_select(self) -> str:
        return os.getenv("FREQ", "E")
    
    @property
    def log_level(self) -> int:
        return int(os.getenv("LOG_LEVEL", "20"))
    
    @property
    def force_koef(self) -> float:
        return float(os.getenv("FORCE_KOEF", "1"))
    
    @property
    def finish_temper(self) -> int:
        return int(os.getenv("FINISH_TEMPER", "80"))
    
config = Config()
