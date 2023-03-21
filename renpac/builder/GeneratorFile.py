import os

from typing import Dict, List, Optional

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

    def __init__(self, relative_path: str) -> None:
        if GeneratorFile.input_path is None or GeneratorFile.output_path is None:
            raise Exception("Must set input and output paths before creating a generator file")

        # strip extension and tokenize
        tokens: List[str] = os.path.splitext(relative_path)[0].split('/')
        self._module: Optional[str]
        self._name: str
        if len(tokens) == 1:
            self._module = None
            self._name = tokens[0]
        else:
            self._module = tokens[0]
            self._name = tokens[1]

        self._is_dependency: bool = False
        self._dependencies: List['GeneratorFile'] = []
        self._dependency_names: List[str] = []

        source_path: Path = Path(f"{GeneratorFile.input_path}/{relative_path}")
        with open(source_path.get()) as file:
            self._input_lines: List[str] = file.read().splitlines()
        
        if self._module is None:
            rpy_filename = f"{self._name}.gen.rpy"
        else:
            rpy_filename = f"{self._module}/{self._name}.gen.rpy"
        output_path: Path = Path(f"{GeneratorFile.output_path}/{rpy_filename}", check_exists=False)
        super().__init__(output_path, source_path=source_path)

    def __repr__(self) -> str:
        return self._name if self._module is None else f"{self._module}.{self._name}" 

    def __str__(self) -> str:
        return self.__repr__()

    def add_dependency(self, target: str) -> None:
        tokens: List[str] = target.split('.')
        if len(tokens) != 3:
            raise Exception(f"Expected three tokens in dependency target {target}")
        module: str = tokens[1]
        file: str = tokens[2]
        dependency: str = f"{module}.{file}"
        self._dependency_names.append(dependency)

    # TODO make this cleaner
    def check_priority(self) -> None:
        if len(self._input_lines) == 0 or not self._input_lines[0].startswith("#priority"):
            return
        self.set_max_priority(int(self._input_lines[0].split("#priority ", 1)[1]))

    def clear(self) -> None:
        self._dependency_names = []
        self._dependencies = []
        super().clear()

    def extract_dependencies(self) -> None:
        self.clear()
        for line in self._input_lines:
            # dependencies begin "from renpac.X.Y" or # "import # renpac.X.Y"
            # where X is the package and Y is the filename
            if (line.startswith("from") or line.startswith("import")) and "renpac" in line:
                tokens: List[str] = line.split(' ')
                target: str = tokens[1]
                self.add_dependency(target)
            self.add_line(line)
        printv(f"{self}", end='')
        if len(self._dependency_names) == 0:
            print()
        else:
            print(":")
            for dep in self._dependency_names:
                print(f" -- {dep}")

    def is_dependency(self) -> bool:
        return self._is_dependency

    def link_dependencies(self) -> None:
        for dependency_name in self._dependency_names:
            if dependency_name not in GeneratorFile.files:
                raise Exception(f"Missing dependency for {self._name}: '{dependency_name}'")
            dependency = GeneratorFile.files[dependency_name]
            dependency._is_dependency = True
            self._dependencies.append(dependency)

    def name(self) -> str:
        return self._name

    # set priority to at most the given priority
    def set_max_priority(self, priority) -> None:
        self._priority = min(self._priority, priority)
        if self._priority < -999:
            raise Exception(f"Illegal priority for {self._name} - must be in range [-999, 999] to avoid clash with Ren'Py")

    def set_priority(self, priority=0) -> None:
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