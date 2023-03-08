from typing import Callable

from Config import *

class Game:
    _combos = []
    _exits = []
    _items = []
    _rooms = []

    def has_combo(name: str) -> bool:
        return name in Game._combos

    def has_hotspot(name: str) -> bool:
        return name in Game._exits or name in Game._items

    def has_room(name: str) -> bool:
        return name in Game._rooms

    @staticmethod
    def parse_definitions():
        print("parsing definitions")
        for section_name in Config.sections():
            print(f" -- '{section_name}'")
            if '.' not in section_name:
                continue
            parts = section_name.split('.')
            if len(parts) > 2:
                print(f"too many parts to section name '{section_name}")
                continue
            type_name = parts[0]
            element_name = parts[1]
            if type_name == "combo":
                Game._combos.append(element_name)
            elif type_name == "exit":
                Game._exits.append(element_name)
            elif type_name == "item":
                Game._items.append(element_name)
            elif type_name == "room":
                Game._rooms.append(element_name)
            else:
                print(f"unknown type '{type_name}'")
        print(f"combos: {Game._combos}")
        print(f"exits: {Game._exits}")
        print(f"items: {Game._items}")
        print(f"rooms: {Game._rooms}")

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