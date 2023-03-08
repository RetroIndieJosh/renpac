from Config import *
from Script import *

TYPE_STRING = 0
TYPE_LITERAL = 1 # for numbers, functions, and references to other objects
TYPE_BOOL = 2

class VariableMap:
    def __init__(self, config_key: str, python_key: str = None, type: int = TYPE_STRING) -> None:
        self.config_key = config_key
        self.python_key = python_key if python_key is not None else config_key
        self.type = type

    def process(self, section: dict, python_name: str) -> str:
        if section is None or not self.config_key in section:
            print(f"WARN no '{self.config_key}' defined for {section}")
            return None
        if self.type == TYPE_LITERAL:
            value = section[self.config_key].replace(' ', '_')
        elif self.type == TYPE_BOOL:
            value = True if section[self.config_key] == "yes" else False
        else:
            text = section[self.config_key].replace('\n', ' ')
            value = f"\"{text}\""
        Script.add_line(f"{python_name}.{self.python_key} = {value}")

def name_to_python(type: str, name: str) -> str:
    return f"{type}_{name}".replace(' ', '_')

def process_varmaps(varmaps: list, section_key: str, python_name: str):
    section = Config.get_section(section_key)
    for varmap in varmaps:
        varmap.process(section, python_name)