# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from pydantic import field_validator

from scripts.amorts import AmortSchema
from scripts.logger import my_logger


DATE_FORMAT = "%d.%m.%Y"
HEADER_MARKER = 'Время'
FIRST_ROW_MARKER = '*'
END_TEST_MARKER = 'end_test'
FIRST_DATA_LENGTH = 24
DECIMAL_SEPARATOR = ','

TYPE_TEMPER = 'temper'
TYPE_LAB = 'lab'
TYPE_LAB_HAND = 'lab_hand'
TYPE_CONV = 'conv'
TYPE_LAB_CASCADE = 'lab_cascade'


class BaseSchema(AmortSchema):
    time_test: str
    operator_name: str
    operator_rank: str
    type_test: str
    serial_number: str
    flag_push_force: str
    static_push_force: float
    dynamic_push_force: float
    speed: float
    
    @field_validator('*', mode='before')
    @classmethod
    def normalize_decimal(cls, v):
        if isinstance(v, str):
            return v.replace(DECIMAL_SEPARATOR, '.')
        return v


class LabSchema(BaseSchema):
    move_list: list
    force_list: list
    

class ConvSchema(BaseSchema):
    move_list: list
    force_list: list
    
    
class TempSchema(BaseSchema):
    temper_list: list
    recoil_list: list
    comp_list: list
    
    
class CascSchema(BaseSchema):
    recoil_list: list
    comp_list: list
    speed_list: list


class ReadArchive:
    SOURCE_DIR = Path('archive/')
    TYPE_SCHEMA_MAP = {
        TYPE_LAB: LabSchema,
        TYPE_LAB_HAND: LabSchema,
        TYPE_CONV: ConvSchema,
        TYPE_TEMPER: TempSchema,
        TYPE_LAB_CASCADE: LabSchema,
    }
    
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.files_arr: List[Path] = []
        self.files_name_arr: List[str] = []
        self.files_name_sort: List[str] = []
        self._reset_state()
        
    def _reset_state(self) -> None:
        """Reset parsing state variables"""
        self.data_one: Dict[str, Any] = {}
        self.data_two: Dict[str, Any] = {}
        self.type_test: str = ''
        self.lab: List[BaseSchema] = []
        self.conv: List[ConvSchema] = []
        self.temper: List[TempSchema] = []
        self.cascade: List[CascSchema] = []
        self.cascade_meta: Dict[str, Any] = {}
        self.speed_list: List[float] = []
        self.recoil_list: List[float] = []
        self.comp_list: List[float] = []

    def init_arch(self) -> None:
        """Initialize archive files list"""
        try:
            self.files_arr = sorted(self.SOURCE_DIR.glob('*.csv'))
            self.files_name_arr = [f.stem for f in self.files_arr]
            self.files_name_sort = sorted(
                self.files_name_arr,
                key=lambda date: datetime.strptime(date, DATE_FORMAT),
                reverse=True
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize archive: {e}")
            
    def select_file(self, filename: str) -> None:
        """Select and parse archive file"""
        try:
            self._reset_state()
            if filename not in self.files_name_arr:
                self.logger.warning(f"File {filename} not found in archive")
                return

            index = self.files_name_arr.index(filename)
            filepath = self.files_arr[index]

            with open(filepath, encoding='utf-8') as f:
                for data_list in self._read_line_in_archive(f):
                    self._parse_str_archive(data_list)
        except Exception as e:
            self.logger.error(f"Failed to select file: {e}")

    def _read_line_in_archive(self, file) -> Any:
        """Generator that reads and parses CSV lines"""
        for line in file:
            data_list = line.strip().split(';')
            if data_list[0] != HEADER_MARKER:
                yield data_list

    def _parse_str_archive(self, archive_list: List[str]) -> None:
        """Parse archive line and create objects"""
        if not archive_list:
            return

        if archive_list[0] == END_TEST_MARKER:
            if self.type_test == TYPE_LAB_CASCADE:
                self._create_cascade_object()
            return

        if archive_list[0] != FIRST_ROW_MARKER:
            self.data_one = self._parse_first_data(archive_list)
        else:
            self.data_two = self._parse_second_data(archive_list[FIRST_DATA_LENGTH:-1])

        if self.data_one and self.data_two:
            self._create_object_archive(self.data_one, self.data_two)

    def _create_object_archive(self, data_one: Dict[str, Any], 
                               data_two: Dict[str, Any]) -> None:
        """Create schema object from parsed data"""
        try:
            data = {**data_one, **data_two}
            if self.type_test == TYPE_LAB_CASCADE:
                lab_obj = LabSchema(**data)
                self.lab.append(lab_obj)
                
                # casc_data = {
                # **data,
                # 'speed_list': self.speed_list,
                # 'recoil_list': self.recoil_list,
                # 'comp_list': self.comp_list,
                # }
                # casc_obj = CascSchema(**casc_data)
                # self.cascade.append(casc_obj)
            
            else:
                schema_class = self.TYPE_SCHEMA_MAP.get(self.type_test, LabSchema)
                obj = schema_class(**data)

                if self.type_test == TYPE_TEMPER:
                    self.temper.append(obj)
                elif self.type_test == TYPE_LAB or self.type_test == TYPE_LAB_HAND:
                    self.lab.append(obj)
                elif self.type_test == TYPE_CONV:
                    self.conv.append(obj)

            self.data_one = {}
            self.data_two = {}
        except Exception as e:
            self.logger.error(f"Failed to create archive object: {e}")

    def _create_cascade_object(self) -> None:
        """Create cascade schema object"""
        try:
            if not self.cascade_meta:
                self.logger.warning("Cascade meta is empty, skipping cascade creation")
                self._reset_cascade_lists()
                return
        
            casc_data = {**self.cascade_meta,
                         'speed_list': self.speed_list[:],
                         'recoil_list': self.recoil_list[:],
                         'comp_list': self.comp_list[:],
                        }
            self.cascade.append(CascSchema(**casc_data))
            self._reset_cascade_lists()
            self.cascade_meta = {}
            self.data_one = {}
        except Exception as e:
            self.logger.error(f"Failed to create cascade object: {e}")

    def _reset_cascade_lists(self) -> None:
        """Reset cascade list variables"""
        self.speed_list = []
        self.recoil_list = []
        self.comp_list = []

    def _parse_first_data(self, archive_list: List[str]) -> Dict[str, Any]:
        """Parse first part of archive record"""
        try:
            data = self._fill_obj_archive_data(archive_list[:FIRST_DATA_LENGTH])
            self.type_test = archive_list[3]
            
            if self.type_test == TYPE_LAB_CASCADE and not self.cascade_meta:
                self.cascade_meta = data.copy()

            list_key = 'move_list' if self.type_test != TYPE_TEMPER else 'temper_list'

            if self.type_test == TYPE_LAB_CASCADE:
                speed = self._parse_float(archive_list[23])
                self._add_data_cascade_graph(speed=speed)

            data[list_key] = self._parse_float_list(archive_list[FIRST_DATA_LENGTH:-1])
            return data
        except Exception as e:
            self.logger.error(f"Failed to parse first data: {e}")
            return {}

    def _parse_second_data(self, archive_list: List[str]) -> Dict[str, Any]:
        """Parse second part of archive record"""
        try:
            data = {}
            if self.type_test == TYPE_TEMPER:
                recoil_list, comp_list = self._parse_temper_graph(archive_list)
                data['recoil_list'] = recoil_list
                data['comp_list'] = comp_list

            elif self.type_test in (TYPE_LAB, TYPE_LAB_HAND, TYPE_CONV):
                data['force_list'] = self._parse_float_list(archive_list)

            elif self.type_test == TYPE_LAB_CASCADE:
                force_list = self._parse_float_list(archive_list)
                if force_list:
                    data['force_list'] = force_list[:]
                    self._add_data_cascade_graph(
                        recoil=max(force_list), 
                        comp=min(force_list)
                    )

            return data
        except Exception as e:
            self.logger.error(f"Failed to parse second data: {e}")
            return {}

    def _fill_obj_archive_data(self, data: List[str]) -> Dict[str, Any]:
        """Fill object with archive data"""
        try:
            if len(data) < FIRST_DATA_LENGTH:
                self.logger.warning("Insufficient data for archive object")
                return {}

            return {
                'time_test': data[0],
                'operator_name': data[1],
                'operator_rank': data[2],
                'type_test': data[3],
                'name': data[4],
                'serial_number': data[5],
                'min_length': self._parse_float(data[6]),
                'max_length': self._parse_float(data[7]),
                'hod': int(data[8]),
                'speed_one': self._parse_float(data[9]),
                'min_recoil': self._parse_float(data[10]),
                'max_recoil': self._parse_float(data[11]),
                'min_comp': self._parse_float(data[12]),
                'max_comp': self._parse_float(data[13]),
                'speed_two': self._parse_float(data[14]),
                'min_recoil_2': self._parse_float(data[15]),
                'max_recoil_2': self._parse_float(data[16]),
                'min_comp_2': self._parse_float(data[17]),
                'max_comp_2': self._parse_float(data[18]),
                'flag_push_force': data[19],
                'static_push_force': self._parse_float(data[20]),
                'dynamic_push_force': self._parse_float(data[21]),
                'max_temper': self._parse_float(data[22]),
                'speed': self._parse_float(data[23]),
            }
        except Exception as e:
            self.logger.error(f"Failed to fill archive data: {e}")
            return {}

    @staticmethod
    def _parse_float(value: str) -> float:
        """Parse float value with locale support"""
        return float(value.replace(DECIMAL_SEPARATOR, '.'))

    def _parse_float_list(self, data_list: List[str]) -> List[float]:
        """Parse list of float values"""
        try:
            return [self._parse_float(x) for x in data_list if x.strip()]
        except Exception as e:
            self.logger.error(f"Failed to parse float list: {e}")
            return []

    def _add_data_cascade_graph(self, speed: float = None, recoil: float = None, 
                                comp: float = None) -> None:
        """Add data to cascade graph lists"""
        if speed is not None:
            self.speed_list.append(speed)
        if recoil is not None:
            self.recoil_list.append(recoil)
        if comp is not None:
            self.comp_list.append(comp)

    def _parse_temper_graph(self, data_list: List[str]) -> tuple:
        """Parse temperature graph data"""
        try:
            recoil_list = []
            comp_list = []
            for value in data_list:
                value = value.strip('\'"')
                parts = value.replace(DECIMAL_SEPARATOR, '.').split('|')
                if len(parts) >= 2:
                    recoil_list.append(float(parts[0]))
                    comp_list.append(float(parts[1]))
            return recoil_list, comp_list
        except Exception as e:
            self.logger.error(f"Failed to parse temper graph: {e}")
            return [], []
