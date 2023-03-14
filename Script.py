import os

from Config import *

class Script:
    _text = ""

    @staticmethod
    def add_header(header: str) -> None:
        Script._text += f"\n###\n# {header}\n###\n"

    @staticmethod
    def add_line(line: str) -> None:
        Script._text += f"{line}\n"

    @staticmethod
    def clear() -> None:
        Script._text = ""
    
    @staticmethod
    def print() -> None:
        print(Script._text)

    @staticmethod
    def write_file(filename: str) -> None:
        TAB = "    "
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write(
                "# THIS FILE WAS GENERATED BY RENPAC\n"
                "# DO **NOT** MODIFY MANUALLY, AS CHANGES MAY BE OVERWRITTEN!\n"
                "# To make changes, modify:\n"
                f"# {TAB}{Config.filename}\n"
                "# and run the generator again.\n\n"
                "init python:\n"
                f"{TAB}def load_game():\n")
            for line in Script._text.splitlines():
                file.write(f"{TAB}{TAB}{line}")