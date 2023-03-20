from typing import Dict, List

from renpac.builder.Path import Path
from renpac.builder.Script import Script

from renpac.base.printv import *

class GeneratorFile(Script):
    # TODO clean this up by putting it in some other higher level thing that
    # handles the file load and navigation etc. (most of generate.py should be
    # wrapped in class code)
    files: Dict[str, 'GeneratorFile'] = {}

    input_path: str
    output_path: str

    def __init__(self, name: str) -> None:
        if GeneratorFile.input_path is None or GeneratorFile.output_path is None:
            raise Exception("Must set input and output paths before creating a generator file")

        self._name: str = name

        self._is_dependency: bool = False
        self._base_dependency_names: List[str] = []
        self._dependencies: List['GeneratorFile'] = []
        self._dependency_names: List[str] = []

        source_path: Path = Path(f"{GeneratorFile.input_path}/{name}.py")
        with open(source_path.get()) as file:
            self._input_lines: List[str] = file.read().splitlines()
        output_path: Path = Path(f"{GeneratorFile.output_path}/{name}.gen.rpy", check_exists=False)
        super().__init__(output_path, source_path=source_path)

    def add_base_dependency(self, line):
        new_dependencies = line.split("from base import ", 1)[1].split(", ")
        self._base_dependency_names += new_dependencies
        for dep in new_dependencies:
            printv(f"-- [base] {dep}")

    def add_dependency(self, line):
        new_dependencies = line.split("from . import ", 1)[1].split(", ")
        self._dependency_names += new_dependencies
        for dep in new_dependencies:
            printv(f"-- {dep}")

    def check_priority(self):
        if len(self._input_lines) == 0:
            return
        if self._input_lines[0].startswith("#priority"):
            self.set_max_priority(int(self._input_lines[0].split("#priority ", 1)[1]))

    def clear(self):
        self._base_dependency_names = []
        self._dependency_names = []
        self._dependencies = []
        super().clear()

    def extract_dependencies(self):
        self.clear()
        printv(f"{self._name}:")
        for line in self._input_lines:
            if line.startswith("from base import"):
                self.add_base_dependency(line)
                continue
            if line.startswith("from . import"):
                self.add_dependency(line)
                continue
            self.add_line(line)

    def is_dependency(self) -> bool:
        return self._is_dependency

    def link_dependencies(self):
        for dependency_name in self._dependency_names:
            if dependency_name not in GeneratorFile.files:
                raise Exception(f"Missing dependency for {self._name}: '{dependency_name}'")
            
            dependency = GeneratorFile.files[dependency_name]
            dependency._is_dependency = True
            self._dependencies.append(dependency)

    def name(self):
        return self._name

    # set priority to at most the given priority
    def set_max_priority(self, priority):
        self._priority = min(self._priority, priority)
        if self._priority < -999:
            raise Exception(f"Illegal priority for {self._name} - must be in range [-999, 999] to avoid clash with Ren'Py")

    def set_priority(self, priority=0):
        self.set_max_priority(priority)
        for dependency in self._dependencies:
            dependency.set_priority(priority - 1)

    def write(self) -> None:
        if self.is_empty():
            printv(f"WARNING no lines in GeneratorFile '{self._name}', file will not be created\n"
                   "- did you extract dependencies?")
        printv(f"convert {self._name} at priority {self._priority}")
        super().write()
        printv(f" => {self._output_path} ({len(self._input_lines)} lines)")