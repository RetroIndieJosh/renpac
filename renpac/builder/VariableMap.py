import logging

from typing import List

from configparser import SectionProxy

from renpac.base.Config import Config, ConfigType

from renpac.builder.Script import *

log = logging.getLogger("VariableMap")

# TODO clean this up, combine with Definition in Game.py used for inventory/game
class VariableMap:
    def __init__(self, config_key: str, python_key: Optional[str] = None, 
            config_type: ConfigType = ConfigType.STRING, default: Optional[str] = None) -> None:
        self.config_key: str = config_key
        self.python_key: str = python_key if python_key is not None else config_key
        self.type: ConfigType = config_type
        self._default: Optional[str] = default

    # TODO separate the "write python script" logic from the "process config" logic
    def process(self, section: SectionProxy, python_name: str) -> List[str]:
        lines: List[str] = []
        raw_value: str
        if section is None or not self.config_key in section:
            if self._default is None: 
                log.warning(f"no '{self.config_key}' defined for {section}")
                return []
            raw_value = self._default
        else:
            raw_value = section[self.config_key]
        if self.type == ConfigType.POSITION:
            (x, y) = raw_value.split(' ')
            lines.append(f"{python_name}.rect.set_pos({x}, {y})")
        elif self.type == ConfigType.SIZE:
            (width, height) = raw_value.split(' ')
            lines.append(f"{python_name}.rect.set_size({width}, {height})")
        else:
            value: str
            if self.type == ConfigType.LITERAL:
                value = raw_value.replace(' ', '_')
            elif self.type == ConfigType.BOOL:
                value = "True" if raw_value == "yes" else "False"
            else:
                text = raw_value.replace('\n', ' ')
                value = f"\"{text}\""
            lines.append(f"{python_name}.{self.python_key} = {value}")
        return lines

def process_varmaps(config: Config, varmaps: list, section_key: str, python_name: str) -> List[str]:
    if varmaps is None:
        return
    lines = []
    section = config.get_section(section_key)
    varmap: VariableMap
    for varmap in varmaps:
        new_lines = varmap.process(section, python_name)
        if new_lines is None:
            continue
        lines += new_lines
    return lines