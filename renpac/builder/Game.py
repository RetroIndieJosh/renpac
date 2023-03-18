from dataclasses import dataclass
from typing import Callable
from renpac.base.printv import *
from renpac.builder.Config import *
from renpac.builder.Script import *
from renpac.builder.VariableMap import *

@dataclass(frozen=True)
class Definition:
    is_required: bool
    is_numeric: bool

class Game:
    def __init__(self, output_path):
        self._combos = []
        self._exits = []
        self._items = []
        self._rooms = []
        self._start_room = None

        self._script = Script(output_path)
        self._script.add_line("def load_game():")
        self._script.indent()
    
    def all_combos(self, func: Callable[[str], list[str]]) -> None:
        if self._combos is None:
            print("WARNING: no combinations in game")
        self._script.add_header(f"COMBOS")
        self._script.add_lines(flatten(map(func, self._combos)))
    
    def all_exits(self, func: Callable[[str], list[str]]) -> None:
        if self._exits is None:
            print("WARNING: no exits in game")
        self._script.add_header(f"EXITS")
        self._script.add_lines(flatten(map(func, self._exits)))

    def all_items(self, func: Callable[[str], list[str]]) -> None:
        if self._items is None:
            print("WARNING: no items in game")
        self._script.add_header(f"ITEMS")
        self._script.add_lines(flatten(map(func, self._items)))
    
    def all_rooms(self, func: Callable[[str], list[str]]) -> None:
        if self._rooms is None:
            raise Exception("ERROR game must have at least one room")
        self._script.add_header(f"ROOMS")
        self._script.add_lines(flatten(map(func, self._rooms)))
    
    def finalize(self) -> None:
        self._script.add_header("START ROOM")
        start_room = name_to_python("room", self._start_room)
        self._script.add_line(f"return {start_room}")
    
    def has_combo(self, name: str) -> bool:
        return name in self._combos
    
    def has_exit(self, name: str) -> bool:
        return name in self._exits
    
    def has_hotspot(self, name: str) -> bool:
        return self.has_exit(name) or self.has_item(name)
    
    def has_item(self, name: str) -> bool:
        return name in self._items
    
    def has_room(self, name: str) -> bool:
        return name in self._rooms
    
    def set_output_path(self, path: str) -> None:
        self._script = Script(path)
    
    def _parse_definition(self, type_name: str, element_name: str):
        if type_name == "exit":
            self._exits.append(element_name)
        elif type_name == "item":
            self._items.append(element_name)
        elif type_name == "room":
            self._rooms.append(element_name)
        else:
            printv(f"unknown type '{type_name}'")
    
    def parse_definitions(self) -> None:
        printv("parsing definitions")
        for section_name in Config.sections():
            printv(f" -- '{section_name}'")
            if '.' not in section_name:
                continue
            if '+' in section_name:
                self._combos.append(section_name)
                continue
            parts = section_name.split('.')
            if len(parts) > 2:
                printv(f"WARN too many parts in section name '{section_name}")
                continue
            self._parse_definition(parts[0], parts[1])
    
    def parse_game(self) -> None:
        section = Config.get_section('game')
        for key in section:
            if key == "start":
                self._start_room = section[key]
    
    def get_values(self, section_name: str, required: dict) -> dict:
        section = Config.get_section(section_name)
        values = {}
        for key in section:
            if key in required:
                values[key] = section[key]
            else:
                printv(f"WARN: unknown {section_name} key '{key}'")
        for key in required:
            if key in values:
                if required[key].is_numeric and not values[key].isnumeric():
                    printv(f"ERROR: expected number for '{key}' but got value '{values[key]}'")
            else:
                if required[key].is_required:
                    printv(f"ERROR: missing required key '{key}' in {section_name}")
                else:
                    printv(f"WARN: missing optional key '{key}' in {section_name}")
        
        return values
    
    def parse_inventory(self) -> None:
        required = {
            "anchor": Definition(True, False),
            "depth": Definition(True, True),
            "length": Definition(True, True)
        }
        values = self.get_values("inventory", required)
        valid_anchors = {"bottom", "left", "right", "top"}
        if values['anchor'] not in valid_anchors:
            anchor = f"INVENTORY_{anchor.upper()}"
            printv(f"ERROR: illegal inventory anchor '{anchor}'")
            return
        anchor = f"INVENTORY_{values['anchor'].upper()}"
        length = int(values['length'])
        depth = int(values['depth'])
        self._script.add_header("INVENTORY")
        self._script.add_line(f"Inventory.set_mode({anchor}, {length}, {depth})")
    
    def report_definitions(self) -> None:
        printv(f"{len(self._combos)} combos: {self._combos}")
        printv(f"{len(self._exits)} exits: {self._exits}")
        printv(f"{len(self._items)} items: {self._items}")
        printv(f"{len(self._rooms)} rooms: {self._rooms}")

    def write(self) -> None:
        printv(f"writing game file to '{self._script._output_path}'")
        self._script.write()

def flatten(list: list[list]) -> list:
    if list is None:
        return None
    return [item for sublist in list for item in sublist]