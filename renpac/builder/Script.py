import os
from typing import List

from datetime import datetime

from renpac.base.printv import *

TAB = "    "

class Script:
    def __init__(self, output_path: str, priority: int = 0, source_path: str = None) -> None:
        self._output_path = output_path
        self._text = ""
        self._priority = priority
        self._source_path = source_path
        self._indent = 0

    def add_header(self, header: str) -> None:
        self.add_line(
            "",
            "#######################",
            f"# {header}",
            "#######################"
        )

    def add_line(self, *args: str) -> None:
        for line in args:
            line = line.rstrip()
            if line is None or line == "":
                return
            for _ in range(self._indent):
                self._text += TAB
            self._text += f"{line}\n"

    def clear(self) -> None:
        self._text = ""
    
    def print(self) -> None:
        printv(self._text)

    def indent(self) -> None:
        self._indent += 1

    def indent_reset(self) -> None:
        self._indent = 0

    def is_empty(self) -> bool:
        return self._text is None or self._text == ""

    # TODO should we genericize script to be able to write any script? and put
    # the init [priority] python higher up? maybe RenpyScript(Script)
    def write(self) -> None:
        if len(self._text) == 0:
            return
        # TODO [temp fix] if _path is always a Path, use get() - otherwise remove str()
        path = str(self._output_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            file.write(
                f"# Generated by renpac v0.0 at {datetime.now()}\n"
                "# THIS FILE WAS GENERATED BY RENPAC\n"
                "# DO **NOT** MODIFY MANUALLY, AS CHANGES MAY BE OVERWRITTEN!\n")
            if self._source_path is not None:
                file.write(
                    "# To make changes, modify:\n"
                    f"# {TAB}{self._source_path}\n"
                    "# and run the generator again.\n")
            file.write(f"\ninit {self._priority} python:\n")
            for line in self._text.splitlines():
                file.write(f"{TAB}{line}\n")