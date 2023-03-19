from typing import Callable, Dict, List

from renpac.base.printv import *

from renpac.builder import python

from renpac.builder.Config import *
from renpac.builder.Script import *
from renpac.builder.VariableMap import *

class Game:
    _instance = None

    def __init__(self, output_path):
        if Game._instance is not None:
            raise Exception("Cannot create more than one Game object")

        Game._instance = self

        self._combos = []
        self._exits = []
        self._items = []
        self._rooms = []
        self._start_room = None

        self._script = Script(output_path)
        self._script.add_line("def load_game():")
        self._script.indent()

    @staticmethod
    def instance() -> 'Game':
        return Game._instance

    def items(self) -> List[str]:
        return self._items

    def rooms(self) -> List[str]:
        return self._rooms
    
    # TODO these should be process_ or write_script for, not all_, since they
    # aren't fully genericized
    def all_combos(self, func: Callable[[str], List[str]]) -> None:
        if self._combos is None:
            print("WARNING: no combinations in game")
        self._script.add_header(f"COMBOS")
        self._script.add_lines(flatten(map(func, self._combos)))
    
    def all_exits(self, func: Callable[[str], List[str]]) -> None:
        if self._exits is None:
            print("WARNING: no exits in game")
        self._script.add_header(f"EXITS")
        self._script.add_lines(flatten(map(func, self._exits)))

    def all_items(self, func: Callable[[str], List[str]]) -> None:
        if self._items is None:
            print("WARNING: no items in game")
        self._script.add_header(f"ITEMS")
        self._script.add_lines(flatten(map(func, self._items)))
    
    def all_rooms(self, func: Callable[[str], List[str]]) -> None:
        if self._rooms is None:
            raise Exception("ERROR game must have at least one room")
        self._script.add_header(f"ROOMS")
        self._script.add_lines(flatten(map(func, self._rooms)))

    def default_exit_size(self) -> str:
        return self._default_exit_size

    def default_item_size(self) -> str:
        return self._default_item_size
    
    def finalize(self) -> None:
        self._script.add_header("START ROOM")
        start_room = python.room(self._start_room)
        self._script.add_line(f"return {start_room}")
    
    def has_combo(self, name: str) -> bool:
        return name in self._combos
    
    def has_exit(self, name: str) -> bool:
        return name in self._exits
    
    def has_hotspot(self, name: str) -> bool:
        return self.has_exit(name.strip()) or self.has_item(name.strip())
    
    def has_item(self, name: str) -> bool:
        return name.strip() in self._items
    
    def has_room(self, name: str) -> bool:
        return name.strip() in self._rooms
    
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

    def parse_defaults(self) -> None:
        # store as string to parse later when size is set
        values = Config.parse_section('exit', {'size': ConfigEntry(TYPE_STRING, False)})
        self._default_exit_size = values['size']

        # ditto above
        values = Config.parse_section('item', {'size': ConfigEntry(TYPE_STRING, False)})
        self._default_item_size = values['size']

    def parse_game(self) -> None:
        values = Config.parse_section('game', {'start': ConfigEntry(TYPE_STRING, True)})
        self._start_room = values['start']
    
    def parse_inventory(self) -> None:
        entries = {
            'anchor': ConfigEntry(TYPE_NUMBER, True),
            'depth': ConfigEntry(TYPE_NUMBER, True),
            'length': ConfigEntry(TYPE_NUMBER, True),
            'items': ConfigEntry(TYPE_LIST, False)
        }
        values = Config.parse_section('inventory', entries)
        valid_anchors = ["bottom", "left", "right", "top"]
        if values['anchor'] not in valid_anchors:
            anchor = f"INVENTORY_{anchor.upper()}"
            printv(f"ERROR: illegal inventory anchor '{anchor}'")
            return
        anchor = f"INVENTORY_{values['anchor'].upper()}"
        length = int(values['length'])
        depth = int(values['depth'])
        self._script.add_header("INVENTORY")
        self._script.add_line(f"Inventory.set_mode({anchor}, {length}, {depth})")

        if 'items' in values:
            items: List[str] = values['items'].split(',')
            for item_name in items:
                if not self.has_item(item_name):
                    raise Exception(f"ERROR no item '{item_name}' for initial inventory")
                item_python = python.item(item_name)
                self._script.add_line(f"Inventory.add({item_python})")
    
    def report_definitions(self) -> None:
        printv(f"{len(self._combos)} combos: {self._combos}")
        printv(f"{len(self._exits)} exits: {self._exits}")
        printv(f"{len(self._items)} items: {self._items}")
        printv(f"{len(self._rooms)} rooms: {self._rooms}")

    def write(self) -> None:
        printv(f"writing game file to '{self._script._output_path}'")
        self._script.write()

def flatten(list: List[List]) -> List:
    if list is None:
        return None
    return [item for sublist in list for item in sublist]
