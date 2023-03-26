import logging

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

# TODO remove
from renpac.builder.VariableMap import *

from renpac.builder import python

from renpac.builder.RenpyScript import *

from renpac.builder.room import room_to_python

log = logging.getLogger("Game")

class CodeBlock:
    def __init__(self, header, lines) -> None:
        self._header: str = header
        self._lines: List[str] = lines

        self._builtin: bool = ' ' not in self._header
        self._name: Optional[str] = None if self.is_builtin() else self._header[self._header.index(' ')+1:] 
        self._type: str = self._header.split(' ')[0]

    def is_builtin(self) -> bool:
        # builtin elements like game, inventory, etc. as oppopsed to named
        # elements like room, item, etc.
        return self._builtin

    def add_line(self, line: str):
        self._lines.append(line)

    def header(self) -> str:
        return self._header

    def name(self) -> str:
        return self._name

    def lines(self) -> List[str]:
        return self._lines

    def type(self) -> str:
        return self._type

class CodeLine:
    def __init__(self, number: int, text: str) -> None:
        self._number: int = number
        self._text: str = text.rstrip()

    def is_comment(self) -> bool:
        return self._text.startswith("#")

    def is_indented(self) -> bool:
        # TODO tab validation, allow more types of tabs as long as consistent through file
        return self._text.startswith("    ")
    
    def is_empty(self) -> bool:
        return len(self._text.strip()) == 0

    def number(self) -> int:
        return self._number

    def strip_comment(self) -> None:
        i = self._text.find('#')
        if i < 0:
            return
        self._text = self._text[:i]

    def text(self) -> str:
        return self._text

class Game:
    _instance = None

    def __init__(self, output_path: Path, source_path: Path) -> None:
        if Game._instance is not None:
            raise Exception("Cannot create more than one Game object")

        Game._instance = self

        self._combo_blocks: List[CodeBlock] = []
        self._exit_blocks: List[CodeBlock] = []
        self._item_blocks: List[CodeBlock] = []
        self._room_blocks: List[CodeBlock] = []

        self._start_room: Optional[str] = None

        self._script = RenpyScript(output_path)
        self._script.add_python("def load_game():")
        self._script.indent()

        lines: List[CodeLine] = get_lines(source_path)
        blocks: List[CodeBlock] = get_blocks(lines)
        parse_blocks(blocks)

    @staticmethod
    def instance() -> 'Game':
        if Game._instance is None:
            raise Exception("Tried to access game, but none defined")
        return Game._instance

    def items(self) -> List[str]:
        return self._item_blocks

    def rooms(self) -> List[str]:
        return self._room_blocks
    
    # TODO these should be process_ or write_script for, not all_, since they
    # aren't fully genericized
    def all_combos(self, func: Callable[[str], List[str]]) -> None:
        if self._combo_blocks is None:
            log.warning("no combinations in game")
        self._script.add_header_python(f"COMBOS")
        #self._script.add_line(*flatten(map(func, self._combos)))
    
    def all_exits(self, func: Callable[[str], List[str]]) -> None:
        if self._exit_blocks is None:
            log.warning("no exits in game")
        self._script.add_header_python(f"EXITS")
        #self._script.add_line(*flatten(map(func, self._exits)))

    def all_items(self, func: Callable[[str], List[str]]) -> None:
        if self._item_blocks is None:
            log.warning("no items in game")
        self._script.add_header_python(f"ITEMS")
        #self._script.add_line(*flatten(map(func, self._items)))
    
    def all_rooms(self, func: Callable[[str], List[str]]) -> None:
        if self._room_blocks is None:
            raise Exception("ERROR game must have at least one room")
        self._script.add_header_python(f"ROOMS")
        #self._script.add_line(*flatten(map(func, self._rooms)))

    def default_exit_size(self) -> str:
        return self._default_exit_size

    def default_item_size(self) -> str:
        return self._default_item_size
    
    def finalize(self) -> None:
        if self._start_room is not None:
            self._script.add_header_python("START ROOM")
            start_room = python.room(self._start_room)
        self._script.add_python(f"return {start_room}")
    
    def has_combo(self, name: str) -> bool:
        return name in self._combo_blocks
    
    def has_exit(self, name: str) -> bool:
        return name in self._exit_blocks
    
    def has_hotspot(self, name: str) -> bool:
        return self.has_exit(name.strip()) or self.has_item(name.strip())
    
    def has_item(self, name: str) -> bool:
        return name.strip() in self._item_blocks
    
    def has_room(self, name: str) -> bool:
        return name.strip() in self._room_blocks

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
        log.info(f"{len(self._combo_blocks)} combos")
        for combo in self._combo_blocks:
            log.debug(f"|-- {combo[0]}")
        log.info(f"{len(self._exit_blocks)} exits")
        for exit in self._exit_blocks:
            log.debug(f"|-- {exit[0]}")
        log.info(f"{len(self._item_blocks)} items")
        for item in self._item_blocks:
            log.debug(f"|-- {item[0]}")
        log.info(f"{len(self._room_blocks)} rooms")
        for room in self._room_blocks:
            log.debug(f"|-- {room[0]}")

    def write(self) -> None:
        log.info(f"writing game file to '{self._script._output_path}'")
        self._script.write()

def get_lines(source_path: Path) -> List[CodeLine]:
    lines: List[CodeLine] = []
    line_number: int = 0
    for line in source_path.read_text().splitlines():
        line_number += 1
        line = CodeLine(line_number, line)
        line.strip_comment()
        if not line.is_empty():
            lines.append(line)
    log.info(f"Game script loaded with {len(lines)} loc ({line_number} with blank/comments)")
    return lines

def get_blocks(lines: List[Tuple[int, str]]) -> List[CodeBlock]:
    current_block: Optional[CodeBlock] = None
    blocks: List[CodeBlock] = []
    errors: List[str] = []
    for line in lines:
        if current_block is not None:
            if line.is_indented():
                current_block.add_line(line.text().lstrip())
                continue
            else:
                blocks.append(current_block)
                current_block = None
        if line.is_indented():
            errors.append(f"[{line.number()}] Unexpected indentation")
            continue
        current_block = CodeBlock(line.text(), [])
    log.info(f"{len(blocks)} blocks")
    for block in blocks:
        log.debug(f" -- {block.header}")
    for error in errors:
        log.error(error)
    if len(errors) > 0:
        raise Exception("Errors in game source. Cannot proceed.")
    return blocks

def parse_block(block: CodeBlock) -> Dict[str, str]:
    log.debug(f"parsing {block.type()} block '{block.name()}'")
    parsed_values: Dict[str, str] = {}
    if not block.is_builtin():
        parsed_values['name'] = block.name()
    multiline = None
    for line in block.lines():
        if line.endswith('\\'):
            if multiline is None:
                multiline = line[:-1]
            else:
                multiline += line[:-1]
            continue
        if multiline is not None:
            line = multiline + line
            multiline = None
        if line[0].isupper():
            parsed_values['desc'] = line
        else:
            parsed_values[line.split(' ')[0]] = line[line.index(' ')+1:] 
    for key, val in parsed_values.items():
        log.debug(f"|-- {key}: {val}")
    return parsed_values

def parse_builtin_block(blocks: List[CodeBlock], block_type: str) -> Dict[str, str]:
    log.info(f"** parsing builtin {block_type}")
    blocks_of_type: List[CodeBlock] = [block for block in blocks if block.type() == block_type]
    if len(blocks_of_type) == 0 or not blocks_of_type[0].is_builtin():
        log.error(f"'{block_type}' is not builtin, or no blocks of that type found")
        return None
    if len(blocks_of_type) > 1:
        log.error(f"Can only define '{block_type}' once, but it is defined {len(blocks_of_type)} times.")
        return None
    return parse_block(blocks_of_type[0])

def parse_blocks_of_type(blocks: List[CodeBlock], block_type: str) -> Dict[str, Dict[str, str]]:
    log.info(f"** parsing {block_type}s")
    blocks_of_type: List[CodeBlock] = [block for block in blocks if block.type() == block_type]
    values: Dict[str, Dict[str, str]] = {}
    block: CodeBlock = None
    for block in blocks_of_type:
        values[block.name()] = parse_block(block)
    return values

def parse_blocks(blocks: List[CodeBlock]) -> Dict[str, Dict[str, Dict[str, str]]]:
    log.info("** parsing blocks")
    parsed_blocks: Dict[str, Dict[str, Dict[str, str]]] = {'engine': {}}
    for block_type in ['game', 'inventory', 'exits', 'items']:
        parsed_blocks['engine'][block_type] = parse_builtin_block(blocks, block_type)
    for block_type in ['combo', 'exit', 'item', 'room']:
        parsed_blocks[block_type] = parse_blocks_of_type(blocks, block_type)
    return parsed_blocks

def parse_game(source_path: Path) -> Dict[str, Dict[str, Dict[str, str]]]:
    if Game._instance is not None:
        raise Exception("Cannot create more than one Game object")

    lines: List[CodeLine] = get_lines(source_path)
    blocks: List[CodeBlock] = get_blocks(lines)
    return parse_blocks(blocks)

def to_json(game_data: Dict[str, Dict[str, Dict[str, str]]]):
    import json
    with Path(__file__).parent.joinpath("build", "bardolf.json").open("w") as file:
        json.dump(game_data, file, indent=4)

def to_python(game_data: Dict[str, Dict[str, Dict[str, str]]], game_file_path: Path):
    script: RenpyScript = RenpyScript(Path(__file__).parent.joinpath("build", "bardolf.rpy"), 999, game_file_path)
    for combo in game_data['combo']:
        script.add_python("# " + python.combo(combo.replace('+', 'and')))
    for exit in game_data['exit']:
        script.add_python("# " + python.exit(exit))
    for item in game_data['item']:
        script.add_python("# " + python.item(item))
    for room, data in game_data['room'].items():
        script.add_python(*room_to_python(room, data))
    script.write()