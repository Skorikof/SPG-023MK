from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class RegisterState:
    bits: list[int] = None
    cycle_force: bool = False
    red_light: bool = False
    green_light: bool = False
    lost_control: bool = False
    excess_force: bool = False
    referent: bool = False
    select_temper: bool = False
    safety_fence: bool = False
    traverse_block: bool = False
    state_freq: bool = False
    state_force: bool = False
    yellow_btn: bool = False
    
    
@dataclass(slots=True, frozen=True)
class SwitchState:
    traverse_block_left: bool = False
    traverse_block_right: bool = False
    alarm_highest_position: bool = False
    alarm_lowest_position: bool = False
    highest_position: bool = False
    lowest_position: bool = False
    

@dataclass(slots=True, frozen=True)
class FastStatus:
    force: float = 0.0
    pos: float = 0.0
    state: RegisterState = field(default_factory=RegisterState)
    time_ms: int = 0
    switch: SwitchState = field(default_factory=SwitchState)
    traverse: float = 0.0
    first_t: float = 0.0
    force_a: float = 0.0
    second_t: float = 0.0
