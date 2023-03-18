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
    _combos = []
    _exits = []
    _items = []
    _rooms = []

    _start_room = None

    @staticmethod
    def all_combos(func: Callable[[str], None]) -> None:
        for combo in Game._combos:
            func(combo)

    @staticmethod
    def all_exits(func: Callable[[str], None]) -> None:
        for exit in Game._exits:
            func(exit)

    @staticmethod
    def all_items(func: Callable[[str], None]) -> None:
        for item in Game._items:
            func(item)

    @staticmethod
    def all_rooms(func: Callable[[str], None]) -> None:
        for room in Game._rooms:
            func(room)

    @staticmethod
    def finalize() -> None:
        Script.add_header("START ROOM")
        start_room = name_to_python("room", Game._start_room)
        Script.add_line(f"return {start_room}")

    @staticmethod
    def has_combo(name: str) -> bool:
        return name in Game._combos

    @staticmethod
    def has_exit(name: str) -> bool:
        return name in Game._exits

    @staticmethod
    def has_hotspot(name: str) -> bool:
        return Game.has_exit(name) or Game.has_item(name)

    @staticmethod
    def has_item(name: str) -> bool:
        return name in Game._items

    @staticmethod
    def has_room(name: str) -> bool:
        return name in Game._rooms

    @staticmethod
    def _parse_definition(type_name: str, element_name: str):
        if type_name == "exit":
            Game._exits.append(element_name)
        elif type_name == "item":
            Game._items.append(element_name)
        elif type_name == "room":
            Game._rooms.append(element_name)
        else:
            printv(f"unknown type '{type_name}'")

    @staticmethod
    def parse_definitions() -> None:
        printv("parsing definitions")
        for section_name in Config.sections():
            printv(f" -- '{section_name}'")
            if '.' not in section_name:
                continue
            if '+' in section_name:
                Game._combos.append(section_name)
                continue
            parts = section_name.split('.')
            if len(parts) > 2:
                printv(f"WARN too many parts in section name '{section_name}")
                continue
            Game._parse_definition(parts[0], parts[1])

    @staticmethod
    def parse_game() -> None:
        section = Config.get_section('game')
        for key in section:
            if key == "start":
                Game._start_room = section[key]

    @staticmethod
    def get_values(section_name: str, required: dict) -> dict:
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

    @staticmethod
    def parse_inventory() -> None:
        required = {
            "anchor": Definition(True, False),
            "depth": Definition(True, True),
            "length": Definition(True, True)
        }
        values = Game.get_values("inventory", required)

        valid_anchors = {"bottom", "left", "right", "top"}
        if values['anchor'] not in valid_anchors:
            anchor = f"INVENTORY_{anchor.upper()}"
            printv(f"ERROR: illegal inventory anchor '{anchor}'")
            return
        anchor = f"INVENTORY_{values['anchor'].upper()}"

        length = int(values['length'])
        depth = int(values['depth'])

        Script.add_header("INVENTORY")
        Script.add_line(f"Inventory.set_mode({anchor}, {length}, {depth})")

    @staticmethod
    def report_definitions() -> None:
        printv(f"{len(Game._combos)} combos: {Game._combos}")
        printv(f"{len(Game._exits)} exits: {Game._exits}")
        printv(f"{len(Game._items)} items: {Game._items}")
        printv(f"{len(Game._rooms)} rooms: {Game._rooms}")
