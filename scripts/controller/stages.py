from enum import Enum, auto


class Stage(Enum):
    WAIT = auto()
    WAIT_BUFFER = auto()
    REPEAT_TEST = auto()
    ALARM_TRAVERSE = auto()
    SEARCH_HOD = auto()
    POS_SET_GEAR = auto()
    TRAVERSE_REFERENT = auto()
    INSTALL_AMORT = auto()
    START_POINT_AMORT = auto()
    TEST_MOVE_CYCLE = auto()
    PUMPING = auto()
    TEST_SPEED_ONE = auto()
    TEST_SPEED_TWO = auto()
    TEST_LAB_HAND_SPEED = auto()
    TEST_TEMPER = auto()
    TEST_LAB_CASCADE = auto()
    STOP_GEAR_END_TEST = auto()
    STOP_GEAR_MIN_POS = auto()
    STOP_TEST = auto()
    TEST_PROGRAM = auto()


class TypeTest(Enum):
    LAB = auto()
    LAB_HAND = auto()
    LAB_CASCADE = auto()
    CONV = auto()
    TEMPER = auto()
    SETTINGS = auto()
