import logging

from pathlib import Path
from typing import Optional

from datetime import datetime

from renpac.base.printv import *

from renpac.builder.RenpyScript import RenpyScript

log = logging.getLogger("RenpyScript")

class GameScript(RenpyScript):
    def __init__(self, output_path: Path, priority: int = 0, 
                source_path: Optional[str] = None, 
                indent = 4) -> None:
        self._return_value: str = ""
        super().__init__(output_path, priority, source_path, indent)

    def add_return(self, return_value: str) -> None:
        if len(self._return_value) > 0:
            raise Exception("Cannot set return value in GameScript to " \
            f"'{return_value}' as it already has return value " \
            f"'{self._return_value}'")
        self._return_value = return_value

    def write(self) -> None:
        self._python = ["def load_game():\n"]  \
            + [f"{self._indent_str}{line}" for line in self._python]
        if len(self._return_value) > 0:
            self._python += [f"{self._indent_str}return {self._return_value}"]
        super().write()
