import logging

from typing import Callable, List, Optional, Tuple

from renpac.builder.Script import *
from renpac.builder.VariableMap import *

from renpac.builder import python

log = logging.getLogger("Game")

class Game:
    _instance = None

    def __init__(self, output_path: Path, source_path: Path) -> None:
        if Game._instance is not None:
            raise Exception("Cannot create more than one Game object")

        Game._instance = self

        self._combos: List[str] = []
        self._exits: List[str] = []
        self._items: List[str] = []
        self._rooms: List[str] = []
        self._start_room: Optional[str] = None

        self._script = Script(output_path)
        self._script.add_line("def load_game():")
        self._script.indent()

        self._lines: List[Tuple[int, str]] = []
        line_number: int = 0
        for line in map(lambda line: line.rstrip(), source_path.read_text().splitlines()):
            line_number += 1
            if line.startswith('#') or len(line) == 0:
                continue
            self._lines.append((line_number, line))
        log.info(f"Game script loaded with {len(self._lines)} loc ({line_number} with blank/comments)")

        current_block: Optional[Tuple[str, List[str]]] = None
        self._blocks: List[Tuple(str, List[str])] = []
        errors: List[str] = []
        for num, text in self._lines:
            # TODO tab validation, allow more types of tabs as long as consistent
            if current_block is not None:
                if text.startswith("    "):
                    current_block[1].append(text.lstrip())
                    continue
                else:
                    self._blocks.append(current_block)
                    current_block = None
            if text.startswith(" "):
                errors.append(f"[{num}] Unexpected indentation")
                continue
            current_block = (text, [])
        log.info(f"{len(self._blocks)} blocks")
        for block in self._blocks:
            log.debug(f" -- {block[0]}")

        for error in errors:
            log.error(error)
        if len(errors) > 0:
            raise Exception("Errors in game source. Cannot proceed.")

    @staticmethod
    def instance() -> 'Game':
        if Game._instance is None:
            raise Exception("Tried to access game, but none defined")
        return Game._instance

    def items(self) -> List[str]:
        return self._items

    def rooms(self) -> List[str]:
        return self._rooms
    
    # TODO these should be process_ or write_script for, not all_, since they
    # aren't fully genericized
    def all_combos(self, func: Callable[[str], List[str]]) -> None:
        if self._combos is None:
            log.warning("no combinations in game")
        self._script.add_header(f"COMBOS")
        #self._script.add_line(*flatten(map(func, self._combos)))
    
    def all_exits(self, func: Callable[[str], List[str]]) -> None:
        if self._exits is None:
            log.warning("no exits in game")
        self._script.add_header(f"EXITS")
        #self._script.add_line(*flatten(map(func, self._exits)))

    def all_items(self, func: Callable[[str], List[str]]) -> None:
        if self._items is None:
            log.warning("no items in game")
        self._script.add_header(f"ITEMS")
        #self._script.add_line(*flatten(map(func, self._items)))
    
    def all_rooms(self, func: Callable[[str], List[str]]) -> None:
        if self._rooms is None:
            raise Exception("ERROR game must have at least one room")
        self._script.add_header(f"ROOMS")
        #self._script.add_line(*flatten(map(func, self._rooms)))

    def default_exit_size(self) -> str:
        return self._default_exit_size

    def default_item_size(self) -> str:
        return self._default_item_size
    
    def finalize(self) -> None:
        if self._start_room is not None:
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

    def collect_definitions(self) -> None:
        log.info("** collecting definitions")
        self._combos = [block for block in self._blocks if block[0].startswith('combo')]
        self._exits = [block for block in self._blocks if block[0].startswith('exit')]
        self._items = [block for block in self._blocks if block[0].startswith('item')]
        self._rooms = [block for block in self._blocks if block[0].startswith('room')]

    def parse_defaults(self) -> None:
        # store as string to parse later when size is set
        #values = self._config.parse_section('exit', {'size': ConfigEntry(ConfigType.STRING, False)})
        #self._default_exit_size = values['size']

        # ditto above
        #values = self._config.parse_section('item', {'size': ConfigEntry(ConfigType.STRING, False)})
        #self._default_item_size = values['size']
        pass

    def parse_game(self) -> None:
        #values = self._config.parse_section('game', {'start': ConfigEntry(ConfigType.STRING, True)})
        #self._start_room = values['start']
        pass
    
    def parse_inventory(self) -> None:
        pass
        """
        entries = {
            'anchor': ConfigEntry(ConfigType.STRING, True),
            'depth': ConfigEntry(ConfigType.INT, True),
            'length': ConfigEntry(ConfigType.INT, True),
            'items': ConfigEntry(ConfigType.LIST, False)
        }
        values: Dict[str, str] = self._config.parse_section('inventory', entries)
        valid_anchors = ["bottom", "left", "right", "top"]
        if values['anchor'] not in valid_anchors:
            anchor: str = f"INVENTORY_{anchor.upper()}"
            log.error(f"illegal inventory anchor '{anchor}'")
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
        """
    
    def report_definitions(self) -> None:
        log.info(f"{len(self._combos)} combos")
        for combo in self._combos:
            log.debug(f" -- {combo[0]}")
        log.info(f"{len(self._exits)} exits")
        for exit in self._exits:
            log.debug(f" -- {exit[0]}")
        log.info(f"{len(self._items)} items")
        for item in self._items:
            log.debug(f" -- {item[0]}")
        log.info(f"{len(self._rooms)} rooms")
        for room in self._rooms:
            log.debug(f" -- {room[0]}")

    def write(self) -> None:
        log.info(f"writing game file to '{self._script._output_path}'")
        self._script.write()