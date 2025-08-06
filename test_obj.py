from pydantic import BaseModel

from settings.settings import PrgSettings


class OperatorSchema(BaseModel):
    name: str
    rank: str


class TestObj:
    def __init__(self):
        self._state_dict = {}
        self._switch_dict = {}
        
        self._serial_number = ''
        self._amort = None
        self._buffer_state = ['null', 'null']

        self._force_list = []
        self._move_list = []
        self._force = []
        self._move = []
        self._temper_graph = []
        self._temper_recoil_graph = []
        self._temper_comp_graph = []
        
        self._force_koef = PrgSettings().force_koef
        self._force_clear = 0
        self._force_correct = 0
        self._force_koef_offset = 0
        self._force_offset = 0

        self._counter = 0
        self._move_now = 0
        self._move_traverse = 0
        self._hod_measure = 0
        self._min_point = 0
        self._max_point = 0
        self._start_direction = False
        self._current_direction = False

        self._force_alarm = 0
        self._temper_first = 0
        self._temper_second = 0
        self._temper_max = 0
        self._temper_now = 0

        self._koef_force_list = []
        self._timer_add_koef = None
        self._timer_calc_koef = None

        self._finish_temper = PrgSettings().finish_temper
        self._timer_yellow = None
        self._time_push_yellow = None

        self._state_list = [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self._static_push_force = 0
        self._dynamic_push_force = 0
        self._max_recoil = 0
        self._max_comp = 0

        self._speed_test = 0
        self._speed_cascade = []
        self._power_amort = 0
        self._freq_piston = 0
        