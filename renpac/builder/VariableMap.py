from typing import List

from renpac.base.printv import *

from renpac.base.Config import Config, ConfigType

from renpac.builder.Script import *

# TODO clean this up, combine with Definition in Game.py used for inventory/game
class VariableMap:
    def __init__(self, config_key: str, python_key: str = None, 
            type: int = ConfigType.STRING, default: str = None) -> None:
        self.config_key = config_key
        self.python_key = python_key if python_key is not None else config_key
        self.type = type
        self._default = default

    # TODO separate the "write python script" logic from the "process config" logic
    def process(self, section: dict, python_name: str) -> List[str]:
        lines = []
        if section is None or not self.config_key in section:
            if self._default is None: 
                printv(f"WARN no '{self.config_key}' defined for {section}")
                return None
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
            if self.type == ConfigType.LITERAL:
                value = raw_value.replace(' ', '_')
            elif self.type == ConfigType.BOOL:
                value = True if raw_value == "yes" else False
            else:
                text = raw_value.replace('\n', ' ')
                value = f"\"{text}\""
            lines.append(f"{python_name}.{self.python_key} = {value}")
        return lines

def process_varmaps(config: Config, varmaps: list, section_key: str, python_name: str) -> str:
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