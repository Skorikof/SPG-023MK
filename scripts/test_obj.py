from pydantic import BaseModel


class OperatorSchema(BaseModel):
    name: str
    rank: str


class DataMoveGraph:
    def __init__(self):
        self.force = []
        self.move = []
        
    @classmethod
    def validate(cls, arg):
        return type(arg) is list
    
    def set_data(self, force: list, move: list):
        if self.validate(force) and self.validate(move):
            self.force.extend(force)
            self.move.extend(move)
        
    def set_terminator(self):
        self.force.append('end')
        self.move.append('end')
        
    def clear_data(self):
        self.force = []
        self.move = []
        
    def get_data(self):
        return self.force, self.move
    
    
class DataTemprGraph:
    def __init__(self):
        self.recoil = []
        self.comp = []
        self.temper = []
        
    @classmethod
    def validate(cls, arg):
        return type(arg) in (int, float)
    
    def set_data(self, recoil: float, comp: float, temper: float):
        if self.validate(recoil) and self.validate(comp) and self.validate(temper):
            self.recoil.append(recoil)
            self.comp.append(comp)
            self.temper.append(temper)
        
    def set_terminator(self):
        self.recoil.append('end')
        self.comp.append('end')
        self.temper.append('end')
        
    def clear_data(self):
        self.recoil = []
        self.comp = []
        self.temper = []
        
    def get_data(self):
        return self.recoil, self.comp, self.temper
    

class DataSpeeds:
    def __init__(self):
        self.speeds = {}
    

class DataTest:
    def __init__(self):
        self.type_test = 'hand'
        self.serial_number = ''
        self.amort = None
        self.flag_push_force = False
        self.static_push_force = 0
        self.dynamic_push_force = 0
