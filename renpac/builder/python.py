"""! Functionality and classes for constructing and outputting Python (or
Ren'py) scripts
"""

import logging
import string
import re

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from renpac.base import Config
from renpac.base import text

from renpac.base.printv import *

from renpac.base import Config

log = logging.getLogger("python")

@dataclass(frozen = True)
class Value:
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
class Call:
    func: str
    args: List[Value] = field(default_factory = list)

    def arg_list(self) -> str:
        return ', '.join([arg.to_python() for arg in self.args])

    def add_arg(self, arg: Value):
        self.args.append(arg)

@dataclass(frozen = True)
class Object:
    python_name: str
    init: str
    calls: List[Call] = field(default_factory = list)
    values: Dict[str, Value] = field(default_factory = dict)

    def __repr__(self) -> str:
        return '\n'.join(self.to_python())

    def __str__(self) -> str:
        return self.__repr__()

    def add_call(self, call: Call):
        self.calls.append(call)

    def add_value(self, key: str, value: str, value_type: Config.Type = Config.Type.STRING) -> None:
        if key in self.values:
            log.error(f"Tried to add key {key} to {self.python_name} ScriptObject but it is already defined")
        self.values[key] = Value(value, value_type)
    
    def get_value(self, key: str) -> Optional[str]:
        return self.values[key].value if key in self.values else None

    def to_python(self) -> List[str]:
        init = f"{self.python_name} = {self.init}"
        sorted_calls = sorted(self.calls, key = lambda call: call.func)
        calls = [f"{self.python_name}.{call.func}({call.arg_list()})" for call in sorted_calls]

        sorted_values = dict(sorted(self.values.items())).items()
        values = [f"{self.python_name}.{key} = {value.to_python()}" for key, value in sorted_values]

        return [init] + calls + values

def python_name(type: Optional[str], n: str) -> str:
    n = n.strip()
    chars = re.escape(string.punctuation + string.whitespace)
    n = re.sub('['+chars+']', '_', n)
    while "__" in n:
        n = n.replace("__", "_")
    if type is None:
        return n
    return f"{type}_{n}"

def test_item():
    data = {
        'desc': "A test item.",
        'printed': "Test Item",
        'fixed': False,
        'pos': "98 14",
        'size': "100 150",
    }
    item = parse_item("test_item", data)

    for key in ['desc', 'printed']:
        assert item.values[key].value == data[key]
        assert item.values[key].expected_type == Config.Type.STRING

    assert item.values['fixed'].value == False
    assert item.values['fixed'].expected_type == Config.Type.BOOL

    assert item.calls[0].func == "rect.set_pos"
    assert len(item.calls[0].args) == 1
    assert item.calls[0].args[0].to_python() == '*(98, 14)'
    assert item.calls[0].args[0].expected_type == Config.Type.COORD

    assert item.calls[1].func == "rect.set_size"
    assert len(item.calls[0].args) == 1
    assert item.calls[1].args[0].to_python() == '*(100, 150)'
    assert item.calls[1].args[0].expected_type == Config.Type.COORD

def test_name():
    assert python_name(None, "foo bar") == "foo_bar"
    assert python_name(None, "shebang + bin/bash") == "shebang_bin_bash"
    assert python_name("foo", "bar") ==  "foo_bar"
    assert python_name("foo", "shebang + bin/bash") == "foo_shebang_bin_bash"

def test_room():
    data = {
        'desc': "A test room.",
        'first': "You enter for the first time.",
        'printed': "Test Room",
        'items': "coin, dagger, bottle, bag",
    }
    room = parse_room("test_room", data)

    for key in ['desc', 'first', 'printed']:
        assert room.values[key].value == data[key]
        assert room.values[key].expected_type == Config.Type.STRING

    assert room.calls[0].func == "hotspot_add"
    assert len(room.calls[0].args) == 4

    print(room.calls[0].args)

    assert room.calls[0].args[0].to_python() == 'coin'
    assert room.calls[0].args[0].expected_type == Config.Type.LITERAL
    assert room.calls[0].args[1].to_python() == 'dagger'
    assert room.calls[0].args[1].expected_type == Config.Type.LITERAL
    assert room.calls[0].args[2].to_python() == 'bottle'
    assert room.calls[0].args[2].expected_type == Config.Type.LITERAL
    assert room.calls[0].args[3].to_python() == 'bag'
    assert room.calls[0].args[3].expected_type == Config.Type.LITERAL
