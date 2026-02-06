from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal

from scripts.logger import my_logger


@dataclass(slots=True)
class AlarmConfig:
    """Configuration for alarm types."""
    tag: str
    message: str
    stop_gear: bool = True  # Whether to stop gear motor
    emit_stage: bool = True  # Whether to emit stage_from_alarm
    

class AlarmSignals(QObject):
    stage_from_alarm = Signal(str)
    alarm_traverse = Signal(str)


class AlarmSteps:
    # Alarm type configurations
    ALARM_CONFIGS = {
        'lost_control': AlarmConfig('lost_control', 'lost control', stop_gear=True, emit_stage=True),
        'excess_force': AlarmConfig('excess_force', 'excess force', stop_gear=True, emit_stage=True),
        'safety_fence': AlarmConfig('safety_fence', 'safety fence', stop_gear=True, emit_stage=False),
        'excess_temperature': AlarmConfig('excess_temperature', 'excess temperature', stop_gear=False, emit_stage=False),
    }

    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = AlarmSignals()
        self.flag_alarm_traverse = False

    def _trigger_alarm(self, config: AlarmConfig):
        """Common alarm trigger logic."""
        try:
            # Set alarm state
            self.model.flag_test_launch = False
            self.model.flag_test = False
            self.model.alarm_tag = config.tag
            self.model.flag_alarm = True
            
            # Stop motors if needed
            if config.stop_gear:
                self.model.fc_control(**{'tag': 'stop', 'adr': 1})
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                self.model.reader_stop_test()
                # self.model.flag_bufer = False
                # self.model.clear_data_in_graph()
                # self.model.timer_pars_circle_stop()
                self.model.write_bit_force_cycle(0)
            
            # Visual feedback
            self.model.write_bit_red_light(1)
            
            # Emit signal if needed
            if config.emit_stage:
                self.signals.stage_from_alarm.emit('wait')
            
            # Logging
            self.logger.warning(config.message)
            self.model.status_bar_msg(config.message)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/_trigger_alarm - {e}')

    def step_lost_control(self):
        """Handle lost control alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS['lost_control'])

    def step_excess_force(self):
        """Handle excess force alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS['excess_force'])

    def step_safety_fence(self):
        """Handle safety fence alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS['safety_fence'])

    def step_excess_temperature(self):
        """Handle excess temperature alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS['excess_temperature'])

    def step_alarm_traverse_position(self):
        """Check and handle traverse position alarms."""
        try:
            # Determine alarm direction
            tag = None
            if not self.model.switch_dict.get('alarm_highest_position', False):
                tag = 'up'
            elif not self.model.switch_dict.get('alarm_lowest_position', False):
                tag = 'down'
            
            if tag and not self.flag_alarm_traverse:
                self.flag_alarm_traverse = True
                
                # Set alarm state
                self.model.flag_test_launch = False
                self.model.flag_test = False
                self.model.alarm_tag = f'alarm_traverse_{tag}'
                self.model.flag_alarm = True
                
                # Feedback
                self.model.write_bit_red_light(1)
                self.model.reader_stop_test()
                # self.model.flag_bufer = False
                # self.model.clear_data_in_graph()
                # self.model.timer_pars_circle_stop()
                self.model.write_bit_force_cycle(0)
                
                # Signal with direction
                self.signals.alarm_traverse.emit(tag)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_alarm_traverse_position - {e}')
