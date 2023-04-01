import logging
import os

from pathlib import Path
from typing import List, Optional

from renpac.builder.RenpyScript import RenpyScript

from renpac.base.printv import *

log = logging.getLogger("GeneratorFile")

class GeneratorFile(RenpyScript):
    def __init__(self, input_root: Path, output_root: Path, relative_path: str) -> None:
        tokens: List[str] = os.path.splitext(relative_path)[0].split('/')
        token_count: int = len(tokens)
        if token_count == 0 or token_count > 2:
            raise Exception(f"Expected 1 or 2 tokens in extensionless name of '{relative_path}' but got {token_count}")
        self._module: Optional[str] = tokens[0] if token_count == 2 else None
        self._name: str = tokens[1] if token_count == 2 else tokens[0]

        self._is_dependency: bool = False
        self._dependencies: List['GeneratorFile'] = []
        self._dependency_names: List[str] = []

        source_path: Path = input_root.joinpath(relative_path).resolve(True)
        with open(source_path) as file:
            self._input_lines: List[str] = file.read().splitlines()
        
        rpy_filename: str = f"{self._name}.gen.rpy" if self._module is None else f"{self._module}/{self._name}.gen.rpy"
        output_path: Path = output_root.joinpath(rpy_filename).absolute()

        super().__init__(output_path, source_path=str(source_path))

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
        log.debug(f" -- manual priority for {self}: {self._priority}")

    def clear(self) -> None:
        self._dependency_names = []
        self._dependencies = []
        super().clear()

    def dependency_names(self) -> List[str]:
        return self._dependency_names

    def extract_dependencies(self) -> None:
        self.clear()
        for line in self._input_lines:
            # dependencies begin "from renpac.X.Y" or # "import # renpac.X.Y"
            # where X is the package and Y is the filename
            if (line.startswith("from") or line.startswith("import")) and "renpac" in line:
                tokens: List[str] = line.split(' ')
                target: str = tokens[1]
                self.add_dependency(target)
                continue
            self.add_python(line)
        dep_count: int = len(self._dependency_names)
        log.debug(f"{self} ({dep_count})")
        if dep_count > 0:
            for dep in self._dependency_names:
                log.debug(f" -- {dep}")

    def is_dependency(self) -> bool:
        return self._is_dependency

    def flag_dependency(self) -> None:
        self._is_dependency = True

    def link_dependency(self, dependency: 'GeneratorFile') -> None:
        dependency.flag_dependency()
        self._dependencies.append(dependency)

    def name(self) -> str:
        return self._name

    def priority(self) -> int:
        return self._priority

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
            log.warning(f"no lines in GeneratorFile '{self._name}', file will not be created\n"
                   "- did you skip computing dependencies?")
        log.debug(f"{self}: {self._priority}")
        super().write()
        log.debug(f" => {self._output_path} ({len(self._input_lines)} lines)")