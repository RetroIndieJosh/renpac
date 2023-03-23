import os
from pathlib import Path
from typing import Dict, List, Optional

import renpac.base.files as files

from renpac.base.printv import enable_verbose, printv

from renpac.builder.GeneratorFile import GeneratorFile

class RenpyGen:
    def __init__(self, relative_input_path: str, relative_output_path: str, sub_dirs: List[str] = []):
        self.sub_dirs: List[str] = sub_dirs

        self.input_path = Path(relative_input_path).resolve(True)
        printv("generator input:", self.input_path, self.sub_dirs)

        self.output_path = Path(relative_output_path).resolve()
        printv("generator output:", relative_output_path, self.sub_dirs)

        self.file_map: Dict[str, GeneratorFile] = {}

    def has_sub_dirs(self):
        return len(self.sub_dirs) > 0

    def clean_up(self) -> None:
        if len(self.sub_dirs) == 0:
            files.clear_dir(self.output_path, [".gen.rpy"])
        else:
            for sub_dir in self.sub_dirs:
                sub_path = self.output_path.joinpath(sub_dir)
                files.clear_dir(sub_path, [".gen.rpy"])

    def load(self) -> None:
        printv(f"** loading files")
        filenames: List[str] = files.filter_files(os.listdir(self.input_path), [".py"], ["__init__.py"])
        if self.has_sub_dirs():
            subdir: str
            for subdir in self.sub_dirs:
                sub_path = Path(f"{self.input_path}/{subdir}").absolute()
                subdir_filenames = files.filter_files(os.listdir(sub_path), [".py"], ["__init__.py"])
                filenames += map(lambda filename: f"{subdir}/{filename}", subdir_filenames)

        if(len(filenames) == 0):
            raise Exception(f"no files for generator in '{self.input_path}' {self.sub_dirs}")

        for py_file_name in filenames:
            f = GeneratorFile(self.input_path, self.output_path, py_file_name)
            self.file_map[str(f)] = f
        printv(f"loaded {len(self.file_map)} files")

    def scan_deps(self):
        printv(f"** reading dependencies")
        for file in self.file_map.values():
            file.extract_dependencies()

    def link_deps(self):
        printv(f"** linking dependencies")
        for file in self.file_map.values():
            for dependency_name in file.dependency_names():
                if dependency_name not in self.file_map:
                    raise Exception(f"Missing dependency for {self._name}: '{dependency_name}'")
                dependency = self.file_map[dependency_name]
                file.link_dependency(dependency)

    def calc_priorities(self):
        printv(f"** calculating priorities")
        for file in filter(lambda file: not file.is_dependency(), self.file_map.values()):
            printv(f"  -- root file: {file}")
            file.set_priority()
        printv(f"** checking manual priorities")
        for file in self.file_map.values():
            file.check_priority()

    def write_files(self):
        printv(f"** generating {len(self.file_map)} files")
        files = list(self.file_map.values())
        files.sort(key=lambda file: file.priority())
        for file in files:
            file.write()

    def generate(self) -> None:
        """! Convert python files from input_path to Ren'py files in output_path
            using dependency detection to calculate priority so Ren'py will load all
            Python scripts in the correct order.

        @param input_path The top-level input path containing all .py files.
        @param output_path The output path for all created .rpy files.
        @param input_subdirs If set, get all .py files from these subdirectories
            in addition to the top level directory.
        """

        self.clean_up()
        self.load()
        self.scan_deps()
        self.link_deps()
        self.calc_priorities()
        self.write_files()

        print(f"{len(self.file_map)} files generated")

if __name__ == "__main__":
    enable_verbose()
    generator = RenpyGen("renpac", "renpac/engine/rpy", ["base", "engine"])
    generator.generate()