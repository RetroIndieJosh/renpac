import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from datetime import datetime

from renpac.base import Config
from renpac.base import text

from renpac.base.printv import *

log = logging.getLogger("REnpyScript")

class ScriptValue:
    def __init__(self, type: Config.Type, value: str) -> None:
        self._type: Config.Type = type
        self.value: str = value

    def to_python(self) -> str:
        # TODO additional types
        match self._type:
            case Config.Type.STRING:
                return text.wrap(self.value, '"')
            case Config.Type.LITERAL:
                return self.value
            case Config.Type.BOOL:
                if Config.is_true(self.value):
                    return "True"
                elif Config.is_false(self.value):
                    return "False"
                self.type_error()
            case Config.Type.COORD:
                values = self.value.split(' ')
                return text.wrap(f"{values[0]}, {values[1]}", '(', ')')
            case Config.Type.INT:
                return str(int(self.value))
            case Config.Type.FLOAT:
                return str(float(self.value))
            case Config.Type.LIST:
                return text.wrap(self.value, '[', ']')
        log.error(f"No match for type '{self._type}'")
        return ""

    def type_error(self) -> None:
        log.error(f"Value '{self.value}' invalid for type '{self._type.name}'")

class ScriptObject:
    def __init__(self, name: str, init: str) -> None:
        self._name: str = name
        self._init: str = init

        self._values: Dict[str, ScriptValue] = {}

    def add_value(self, key: str, value: str, value_type: Config.Type = Config.Type.STRING) -> None:
        if key in self._values:
            log.error(f"Tried to add key {key} to {self._name} ScriptObject but it is already defined")
        self._values[key] = ScriptValue(value_type, value)

    def to_python(self) -> List[str]:
        sorted_values = dict(sorted(self._values.items())).items()
        return [self._init] + [f"{self._name}.{key} = {value.to_python()}" for key, value in sorted_values]

class RenpyScript:
    def __init__(self, output_path: Path, priority: int = 0, 
                source_path: Optional[str] = None, 
                indent = 4) -> None:
        self._output_path: Path = output_path
        self._priority: int = priority
        self._source_path: Optional[str] = source_path
        self._indent_str: str = ' ' * indent

        self._script_objects: List[ScriptObject] = []
        self._python: List[str] = []
        self._renpy: List[str] = []

    def add_header(self, header: str, python: bool = True) -> None:
        header_lines: List[str] = [
            "",
            "#######################",
            f"# {header}",
            "#######################"]
        if python:
            self.add_python(*header_lines)
        else:
            self.add_renpy(*header_lines)

    def add_object(self, script_object: ScriptObject) -> None:
        self.add_python(*script_object.to_python())

    def add_python(self, *args: str) -> None:
        self._python += [f"{line}\n" for line in list(args)]
    
    def add_renpy(self, *args: str) -> None:
        self._renpy += [f"{line}\n" for line in list(args)]

    def clear(self) -> None:
        self._python = []
        self._renpy = []
    
    def print(self) -> None:
        printv(self._python)
        printv(self._renpy)

    def is_empty(self) -> bool:
        return len(self._python) + len(self._renpy) == 0

    # TODO should we genericize script to be able to write any script? and put
    # the init [priority] python higher up? maybe RenpyScript(Script)
    def write(self) -> None:
        if self.is_empty():
            return
        self._output_path.parent.mkdir(exist_ok = True)
        with open(self._output_path, "w") as file:
            file.writelines([
                f"# Generated by renpac v0.0 at {datetime.now()}\n",
                "# THE FOLLOWING WAS GENERATED BY RENPAC\n",
                "# DO **NOT** MODIFY MANUALLY, AS CHANGES MAY BE OVERWRITTEN!\n"])
            if self._source_path is not None:
                file.writelines([
                    "\n# To make changes, modify:\n",
                    f"# {self._indent_str}{self._source_path}\n",
                    "# and run the generator again.\n"])
            file.writelines(self._renpy)
            file.write(f"\ninit {self._priority} python:\n")
            file.writelines([f"{self._indent_str}{line}" for line in self._python])

if __name__ == "__main__":
    path: Path = Path(__file__).parent.joinpath("test.gen.rpy")

    indent_str = input("Indent? (blank for default) ")
    indent = 4 if indent_str == "" else int(indent_str)

    script = RenpyScript(path, 89, "RenpyScript test function", indent)

    script.add_header("test python header")
    script.add_header("test renpy header", False)
    script.add_python("test python line")
    script.add_renpy("test renpy line")

    foo = ScriptObject("foo", "foo = Bar('foo')")
    foo.add_value("num", "4", Config.Type.INT)
    foo.add_value("float", "45.872", Config.Type.FLOAT)
    foo.add_value("coord", "82 99", Config.Type.COORD)
    foo.add_value("string", "A foobar", Config.Type.STRING)
    foo.add_value("truth", "yes", Config.Type.BOOL)
    foo.add_value("truth2", "True", Config.Type.BOOL)
    foo.add_value("truth3", "1", Config.Type.BOOL)
    foo.add_value("lies", "no", Config.Type.BOOL)
    foo.add_value("lies2", "fAlSe", Config.Type.BOOL)
    foo.add_value("lies3", "0", Config.Type.BOOL)
    script.add_object(foo)

    script.write()

    EXPECTED_LINES = 23
    line_count = len(path.read_text().splitlines())
    if line_count == EXPECTED_LINES:
        print(f"Line count matches.")
    else:
        print(f"Something went wrong. Expected {EXPECTED_LINES} lines but wrote {line_count}.")

    input(f"Test file written to {path}.\nPress enter to delete and end tests.")
    path.unlink()