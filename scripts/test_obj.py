from pydantic import BaseModel

from scripts.settings import PrgSettings


class OperatorSchema(BaseModel):
    name: str
    rank: str


class DataMoveGraph:
    def __init__(self):
        self.force = []
        self.move = []
        self.dynamic_push_force = 0
        
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

    def set_dynamic_push_force(self, force):
        self.dynamic_push_force = force
        
    def clear_data(self):
        self.force = []
        self.move = []
        
    def get_data(self):
        return self.force, self.move

    def get_dynamic_push_force(self):
        return self.dynamic_push_force
    
    
class DataTemprGraph:
    def __init__(self):
        self.recoil = []
        self.comp = []
        self.temper = []
        self.dynamic_push_force = 0
        
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
        self.amort = None
        self.type_test = 'hand'
        self.operator = OperatorSchema(name='', rank='')
        self.serial = ''
        self.speed_test = 0
        self.speed_list = []
        self.force_alarm = 0
        self.flag_push_force = False
        self.static_push_force = 0
        self.temperature = 0
        self.first_temperature = 0
        self.second_temperature = 0
        self.max_temperature = 0
        self.finish_temperature = PrgSettings().finish_temper

        self.data_test = {}
