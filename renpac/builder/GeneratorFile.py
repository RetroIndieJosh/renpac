import os

from datetime import datetime

from renpac.base.printv import *

class GeneratorFile:
    # TODO clean this up by putting it in some other higher level thing that
    # handles the file load and navigation etc. (most of generate.py should be
    # wrapped in class code)
    files = {}

    input_path = None
    output_path = None

    def __init__(self, name) -> None:
        if GeneratorFile.input_path is None:
            raise Exception("Must set input path before creating a generator file")

        self.name = name
        with open(f"{GeneratorFile.input_path}/{name}.py") as file:
            self.lines = file.read().splitlines()
        self.priority = 0
        self.is_dependency = False
        self.base_dependency_names = []
        self.dependencies = []
        self.dependency_names = []

    def check_priority(self):
        if len(self.lines) == 0:
            return
        if self.lines[0].startswith("#priority"):
            self.set_max_priority(int(self.lines[0].split("#priority ", 1)[1]))

    def add_base_dependency(self, line):
        self.base_dependency_names = line.split("from base import ", 1)[1].split(", ")

    def find_dependencies(self):
        printv(f"{self.name}:")
        for line in self.lines:
            if line.startswith("from base import"):
                self.add_base_dependency(line)
            if not line.startswith("from . import"):
                continue
            self.dependency_names = line.split("from . import ", 1)[1].split(", ")

    def link_dependencies(self):
        for dependency_name in self.dependency_names:
            if dependency_name not in GeneratorFile.files:
                raise Exception(f"Missing dependency for {self.name}: '{dependency_name}'")
            
            dependency = GeneratorFile.files[dependency_name]
            dependency.is_dependency = True
            self.dependencies.append(dependency)

    # set priority to at most the given priority
    def set_max_priority(self, priority):
        self.priority = min(self.priority, priority)
        if self.priority < -999:
            raise Exception(f"Illegal priority for {self.name} - must be in range [-999, 999] to avoid clash with Ren'Py")

    def set_priority(self, priority=0):
        self.set_max_priority(priority)
        for dependency in self.dependencies:
            dependency.set_priority(priority - 1)

    def write(self) -> None:
        if GeneratorFile.output_path is None:
            raise Exception("Must set output path before writing a generator file")

        os.makedirs(GeneratorFile.output_path, exist_ok=True)

        printv(f"convert {self.name} at priority {self.priority}")
        with open(f"{GeneratorFile.output_path}/{self.name}.gen.rpy", "w") as file:
            file.write(f"# Generated by renpy-python-generator v0.0 at {datetime.now()}\n")
            file.write("# THIS FILE WAS GENERATED! DO NOT MODIFY MANUALLY AS CHANGES MAY BE OVERWRITTEN\n")
            file.write(f"# To make changes, modify {self.name}.py and run the generator again.\n\n")
            file.write(f"init {self.priority} python:\n")
            for line in self.lines:
                file.write(f"    {line}\n")
        printv(f" => {self.name}.gen.rpy ({len(self.lines)} lines)")