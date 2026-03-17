# -*- coding: utf-8 -*-
import traceback
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal

from scripts.logger import my_logger
from .stages import Stage, TypeTest
from scripts.model import Model


@dataclass
class AlarmConfig:
    """Configuration for alarm types."""
    tag: str
    stop_gear: bool = True
    emit_stage: bool = True
    

class AlarmType(str, Enum):
    LOST_CONTROL = "lost_control"
    EXCESS_FORCE = "excess_force"
    SAFETY_FENCE = "safety_fence"
    EXCESS_TEMPERATURE = "excess_temperature"


class AlarmSignals(QObject):
    stage_from_alarm = Signal(object)
    alarm_traverse = Signal(str)


class AlarmSteps:
    ALARM_CONFIGS = {
        AlarmType.LOST_CONTROL: AlarmConfig(AlarmType.LOST_CONTROL,
                                            stop_gear=True, emit_stage=True),
        AlarmType.EXCESS_FORCE: AlarmConfig(AlarmType.EXCESS_FORCE,
                                            stop_gear=True, emit_stage=True),
        AlarmType.SAFETY_FENCE: AlarmConfig(AlarmType.SAFETY_FENCE,
                                            stop_gear=True, emit_stage=False),
        AlarmType.EXCESS_TEMPERATURE: AlarmConfig(AlarmType.EXCESS_TEMPERATURE,
                                                  stop_gear=False, emit_stage=False),
    }

    def __init__(self, model: Model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = AlarmSignals()
        self.flag_alarm_traverse = False
        
    def _stop_gear(self):
        self.model.fc_control(tag="stop", adr=1)
        self.model.fc_control(tag="stop", adr=2)
        self.model.stop_collect()
        if self.model.get_type_test() == TypeTest.LAB_CASCADE:
            self.model.write_end_test_in_archive()

    def _set_common_alarm_flags(self, tag: str):
        self.model.flag_test_launch = False
        self.model.flag_test = False
        self.model.alarm_tag = tag
        self.model.flag_alarm = True

    def _trigger_alarm(self, config: AlarmConfig):
        try:
            self._set_common_alarm_flags(config.tag.value)

            if config.stop_gear:
                self._stop_gear()

            self.model.write_bit_red_light(1)

            if config.emit_stage:
                self.signals.stage_from_alarm.emit(Stage.WAIT)

            self.logger.warning(config.tag.value)

        except Exception:
            self.logger.error(traceback.format_exc())

    def step_lost_control(self):
        """Handle lost control alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS[AlarmType.LOST_CONTROL])

    def step_excess_force(self):
        """Handle excess force alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS[AlarmType.EXCESS_FORCE])

    def step_safety_fence(self):
        """Handle safety fence alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS[AlarmType.SAFETY_FENCE])

    def step_excess_temperature(self):
        """Handle excess temperature alarm."""
        self._trigger_alarm(self.ALARM_CONFIGS[AlarmType.EXCESS_TEMPERATURE])

    # FIXME Проверить вот этот моент
    def step_alarm_traverse_position(self):
        """Check and handle traverse position alarms."""
        try:
            tag = None
            if not self.model.switch_dict.get('alarm_highest_position', False):
                tag = 'up'
            elif not self.model.switch_dict.get('alarm_lowest_position', False):
                tag = 'down'
            
            if tag and not self.flag_alarm_traverse:
                self.flag_alarm_traverse = True
                msg = f'alarm_traverse_{tag}'
                self._set_common_alarm_flags(self, msg)

                self.model.write_bit_red_light(1)
                self.model.stop_collect()

                self.signals.alarm_traverse.emit(tag)

        except Exception as e:
            self.logger.error(e)

    def reset_traverse_alarm_flag(self):
        self.flag_alarm_traverse = False
    
    def control_alarm_state(self):
        """Check for alarm conditions and return alarm tag or None."""
        try:
            # Check state_dict alarms first (higher priority)
            alarm_checks = [
                ('lost_control', self.model.state_dict.get('lost_control', False)),
                ('excess_force', self.model.state_dict.get('excess_force', False)),
                ('safety_fence', self.model.state_dict.get('safety_fence', False)),
            ]
            
            for alarm_tag, is_triggered in alarm_checks:
                if is_triggered:
                    return alarm_tag
            
            # Check temperature alarm (only if not in temperature test)
            if self.model.get_type_test() != TypeTest.TEMPER:
                if self.model.data_test.max_temperature >= self.model.data_test.amort.max_temper:
                    return 'excess_temperature'
            
            return None

        except Exception as e:
            self.logger.error(e)
