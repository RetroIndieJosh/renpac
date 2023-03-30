import logging

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from renpac.base import Config
from renpac.base import text

from renpac.base.printv import *

log = logging.getLogger("scripting")

@dataclass(frozen = True)
class ScriptValue:
    value: str
    expected_type: Config.Type = Config.Type.STRING

    def __repr__(self) -> str:
        return self.to_python()

    def __str__(self) -> str:
        return self.__repr__()

    def to_python(self) -> str:
        value = self.value.strip()
        match self.expected_type:
            case Config.Type.STRING:
                return text.wrap(value, '"')
            case Config.Type.LITERAL:
                return value
            case Config.Type.BOOL:
                if Config.is_true(value):
                    return "True"
                elif Config.is_false(value):
                    return "False"
                self.type_error()
            case Config.Type.COORD:
                values = value.split(' ')
                x = int(values[0])
                y = int(values[1])
                if x < 0 or y < 0:
                    raise Exception("Coordinates may not be negative.")
                return f"*({values[0]}, {values[1]})"
            case Config.Type.INT:
                return str(int(value))
            case Config.Type.FLOAT:
                return str(float(value))
            case Config.Type.LIST:
                return text.wrap(value, '[', ']')
        log.error(f"No match for type '{self.expected_type}'")
        return ""

    def type_error(self) -> None:
        log.error(f"Value '{self.value}' invalid for type '{self.expected_type.name}'")

@dataclass(frozen = True)
class ScriptCall:
    func: str
    args: List[ScriptValue] = field(default_factory = list)

    def arg_list(self) -> str:
        return ', '.join([arg.to_python() for arg in self.args])

    def add_arg(self, arg: ScriptValue):
        self.args.append(arg)

@dataclass(frozen = True)
class ScriptObject:
    python_name: str
    init: str
    calls: List[ScriptCall] = field(default_factory = list)
    values: Dict[str, ScriptValue] = field(default_factory = dict)

    def __repr__(self) -> str:
        return '\n'.join(self.to_python())

    def __str__(self) -> str:
        return self.__repr__()

    def add_call(self, call: ScriptCall):
        self.calls.append(call)

    def add_value(self, key: str, value: str, value_type: Config.Type = Config.Type.STRING) -> None:
        if key in self.values:
            log.error(f"Tried to add key {key} to {self.python_name} ScriptObject but it is already defined")
        self.values[key] = ScriptValue(value, value_type)
    
    def get_value(self, key: str) -> Optional[str]:
        return self.values[key].value if key in self.values else None

    def to_python(self) -> List[str]:
        init = f"{self.python_name} = {self.init}"
        sorted_calls = sorted(self.calls, key = lambda call: call.func)
        calls = [f"{self.python_name}.{call.func}({call.arg_list()})" for call in sorted_calls]

        sorted_values = dict(sorted(self.values.items())).items()
        values = [f"{self.python_name}.{key} = {value.to_python()}" for key, value in sorted_values]

        return [init] + calls + values
