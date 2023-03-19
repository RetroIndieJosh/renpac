from renpac.base.printv import *

from renpac.builder.Config import *
from renpac.builder.Script import *

TYPE_STRING = 0
TYPE_LITERAL = 1 # for numbers, functions, and references to other objects
TYPE_BOOL = 2
TYPE_POSITION = 3
TYPE_SIZE = 4

# TODO clean this up, combine with Definition in Game.py used for inventory/game
class VariableMap:
    def __init__(self, config_key: str, python_key: str = None, type: int = TYPE_STRING, default: str = None) -> None:
        self.config_key = config_key
        self.python_key = python_key if python_key is not None else config_key
        self.type = type
        self._default = default

    def process(self, section: dict, python_name: str) -> List[str]:
        lines = []
        if section is None or not self.config_key in section:
            if self._default is None: 
                printv(f"WARN no '{self.config_key}' defined for {section}")
                return None
            raw_value = self._default
        else:
            raw_value = section[self.config_key]
        if self.type == TYPE_POSITION:
            (x, y) = raw_value.split(' ')
            lines.append(f"{python_name}.rect.set_pos({x}, {y})")
        elif self.type == TYPE_SIZE:
            (width, height) = raw_value.split(' ')
            lines.append(f"{python_name}.rect.set_size({width}, {height})")
        else:
            if self.type == TYPE_LITERAL:
                value = raw_value.replace(' ', '_')
            elif self.type == TYPE_BOOL:
                value = True if raw_value == "yes" else False
            else:
                text = raw_value.replace('\n', ' ')
                value = f"\"{text}\""
            lines.append(f"{python_name}.{self.python_key} = {value}")
        return lines

def combo_to_python(name: str) -> str:
    return name_to_python("combo", name)

def exit_to_python(name: str) -> str:
    return name_to_python("exit", name)
    
def item_to_python(name: str) -> str:
    return name_to_python("item", name)

def room_to_python(name: str) -> str:
    return name_to_python("room", name)

def name_to_python(type: str, name: str) -> str:
    return f"{type}_{name.strip()}".replace(' ', '_')

def process_varmaps(varmaps: list, section_key: str, python_name: str) -> str:
    if varmaps is None:
        return
    lines = []
    section = Config.get_section(section_key)
    varmap: VariableMap
    for varmap in varmaps:
        new_lines = varmap.process(section, python_name)
        if new_lines is None:
            continue
        lines += new_lines
    return lines