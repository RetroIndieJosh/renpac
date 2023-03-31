import logging
import os

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TypeAlias

from renpac.base import Config
from renpac.base import target

from renpac.base.StaticClass import StaticClass

from renpac.builder import python

from renpac.builder.GameScript import GameScript
from renpac.builder.VariableMap import VariableMap, map_varmaps

# globals
log = logging.getLogger("Game")

class IssueLevel(Enum):
    INFO = 0,
    WARNING = 1,
    ERROR = 2

@dataclass()
class BuildIssue:
    message: str
    line: int
    level: IssueLevel

    def is_error(self) -> bool:
        return self.level == IssueLevel.ERROR

    def is_warning(self) -> bool:
        return self.level == IssueLevel.WARNING

    def print(self) -> None:
        color: str = ""
        if self.level == IssueLevel.WARNING:
            color = "\033[93m"
        elif self.level == IssueLevel.ERROR:
            color = "\033[91m"
        elif self.level == IssueLevel.INFO:
            color = "\033[96m"
        print(f"{color}[{self.level.name}]", end='')
        if self.line >= 0:
            print(f" Line {self.line}", end='')
        print(f": {self.message}")

class BuildIssueManager(StaticClass):
    _issues: List[BuildIssue] = []

    @staticmethod
    def add_error(error: str, line: int = -1):
        BuildIssueManager.add_issue(error, line, IssueLevel.ERROR)
        log.error(error)

    @staticmethod
    def add_issue(message: str, line: int, level: IssueLevel):
        issue: BuildIssue = BuildIssue(message, line, level)
        BuildIssueManager._issues.append(issue)

    @staticmethod
    def add_info(info: str, line: int = -1):
        BuildIssueManager.add_issue(info, line, IssueLevel.INFO)
        log.warn(info)

    @staticmethod
    def add_warning(warning: str, line: int = -1):
        BuildIssueManager.add_issue(warning, line, IssueLevel.WARNING)
        log.warn(warning)

    @staticmethod
    def count_errors() -> int:
        return sum(issue.is_error() for issue in BuildIssueManager._issues)

    @staticmethod
    def count_warnings() -> int:
        return sum(issue.is_error() for issue in BuildIssueManager._issues)

    @staticmethod
    def has_error():
        return BuildIssueManager.count_errors() > 0

    @staticmethod
    def has_warning():
        return BuildIssueManager.count_warnings() > 0

    @staticmethod
    def print() -> None:
        os.system("color")
        print("************ BUILD MESSAGES ************")
        for issue in BuildIssueManager._issues:
            issue.print()

        error_count = BuildIssueManager.count_errors()
        warning_count = BuildIssueManager.count_warnings()
        print(f"\033[0m{error_count} errors, {warning_count} warnings")
        print("************ END BUILD MESSAGES ************")

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
        return self._text.strip()

class CodeBlock:
    def __init__(self, header, lines, start_line) -> None:
        self._header: str = header
        self._start_line = start_line
        self._lines: List[CodeLine] = lines

        self._builtin: bool = ' ' not in self._header
        self._name: Optional[str] = None if self.is_builtin() else self._header[self._header.index(' ')+1:] 
        self._type: str = self._header.split(' ')[0]

    def add_line(self, line: CodeLine):
        self._lines.append(line)

    def header(self) -> str:
        return self._header

    def is_builtin(self) -> bool:
        # builtin elements like game, inventory, etc. as oppopsed to named
        # elements like room, item, etc.
        return self._builtin

    def name(self) -> Optional[str]:
        return self._name

    def lines(self) -> List[CodeLine]:
        return self._lines

    def start_line(self) -> int:
        return self._start_line

    def type(self) -> str:
        return self._type

# type aliases
BlockData: TypeAlias = Dict[str, CodeLine]
SectionData: TypeAlias = Dict[str, BlockData]
GameData: TypeAlias = Dict[str, SectionData]

class Game:
    def __init__(self, source_path: Path) -> None:
        lines: List[CodeLine] = get_lines(source_path)
        blocks: List[CodeBlock] = get_blocks(lines)
        self._data: GameData = parse_game(blocks)

        self.load_game()
        self.load_inventory()
        self.load_defaults()

    def check_loaded(self, operation: str) -> bool:
        is_loaded = len(self._data) > 0
        if not is_loaded:
            log.error(f"Cannot {operation}, game is not loaded")
        return is_loaded

    def defaults(self, game_data: GameData) -> BlockData:
        return game_data['global']['defaults']

    def dump_to_log(self) -> None:
        from pprint import pformat
        for line in pformat(self._data).splitlines():
            log.debug(line)

    # TODO None checks
    # TODO parse as coord so width can != height 
    def load_defaults(self) -> None:
        self._default_exit_size = int(self.get_value('engine', 'exits', 'size'))
        self._default_item_size = int(self.get_value('engine', 'items', 'size'))

    def get_value(self, section_key: str, block_key: str, value_key: str, required: bool = False) -> str:
        fail: str = ""
        if section_key in self._data:
            section = self._data[section_key]
            if block_key in section:
                block = section[block_key]
                if value_key in block:
                    return block[value_key].text().strip()
                fail = f"value '{section_key}.{block_key}.{value_key}'"
            else:
                fail = f"block '{section_key}.{block_key}'"
        else:
            fail = f"section '{section_key}'"
        if required:
            BuildIssueManager.add_error(f"Could not find required {fail} in game data")
        else:
            BuildIssueManager.add_warning(f"Could not find optional {fail} in game data")
        return ""

    def load_game(self) -> None:
        log.info("** loading game definitions")
        self._name = self.get_value('engine', 'game', 'desc')
        log.debug(f"Name: {self._name}")
        self._start_room = self.get_value('engine', 'game', 'start', True)
        log.debug(f"Start room: {self._start_room}")

    def load_inventory(self) -> None:
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

    def get_exits(self) -> List[str]:
        return [exit for exit in self._data['exit']]

    def get_hotspots(self) -> List[str]:
        return self.get_exits() + self.get_hotspots()

    def get_items(self) -> List[str]:
        return [item for item in self._data['item']]

    def get_rooms(self) -> List[str]:
        return [room for room in self._data['room']]

    def has_exit(self, exit_name: str) -> bool:
        return exit_name in self.get_exits()

    def has_hotspot(self, hotspot_name: str) -> bool:
        return hotspot_name in self.get_hotspots()

    def has_item(self, item_name: str) -> bool:
        return item_name in self.get_items()

    def has_room(self, room_name: str) -> bool:
        return room_name in self.get_rooms()

    def parse_combo(self, combo_name: str, combo_data: BlockData) -> python.Object:
        combo_varmaps: List[VariableMap] = [
            VariableMap('message'),
            VariableMap('with', 'replace_with'),
        ]

        combo_name_python = python.python_name('combo', combo_name.replace('+', 'and'))
        combo: python.Object = python.Object(combo_name_python, "Combination()")
        map_varmaps(combo, combo_varmaps, {key: combo_data[key].text() for key in combo_data})

        flags: int = target.TARGET_NONE
        key: str
        for key in ['delete', 'replace']:
            if key in combo_data:
                key_target = combo_data[key]
                if key_target == 'none':
                    flags = target.TARGET_NONE
                elif key_target == 'self':
                    flags = target.TARGET_SELF
                elif key_target == 'other':
                    flags = target.TARGET_OTHER
                elif key_target == 'both':
                    flags = target.TARGET_SELF | target.TARGET_OTHER
            combo.add_value(key, str(flags), value_type=Config.Type.INT)

        # error checking

        if combo.get_value('replace_with') is not None and combo.get_value('replace') == target.TARGET_NONE:
            line = combo_data['replace'].number()
            BuildIssueManager.add_warning(f"'with' defined in '{combo_name}' but 'replace' is set to 'none'", line)

        if combo.get_value('replace_with') is None and combo.get_value('replace') != target.TARGET_NONE:
            line = combo_data['replace'].number() if 'replace' in combo_data else -1
            BuildIssueManager.add_warning(f"'replace' defined in '{combo_name}' but no 'with' set", line)

        # ignore delete flag if it's the same as replace
        if combo.get_value('delete') == combo.get_value('replace'):
            combo.values['delete'] = python.Value(str(target.TARGET_NONE), Config.Type.INT)

        return combo

    def parse_exit(self, exit_name: str, exit_data: BlockData) -> python.Object:
        exit_varmaps: List[VariableMap] = [
            VariableMap("message"),
            VariableMap("location", required=True),
            VariableMap("target", required=True),
        ]

        exit = python.Object(python.python_name("exit", exit_name), f"exit(\"{exit_name}\")")
        map_varmaps(exit, exit_varmaps, {key: exit_data[key].text() for key in exit_data})

        if 'pos' in exit_data:
            set_pos: python.Call = python.Call("rect.set_pos")
            set_pos.add_arg(python.Value(exit_data['pos'].text(), Config.Type.COORD))
            exit.add_call(set_pos)
        else:
            BuildIssueManager.add_error(f"exit {exit.python_name} has no position defined", 
                list(exit_data.values())[0].number())

        if 'size' in exit_data:
            set_size: python.Call = python.Call("rect.set_size")
            set_size.add_arg(python.Value(exit_data['size'].text(), Config.Type.COORD))
            exit.add_call(set_size)

        # TODO add TYPE_ROOM to handle this
        rooms = self.get_rooms()
        if exit.values['location'] not in rooms:
            line = exit_data['location'].number()
            log.info(f"location line: {line}")
            BuildIssueManager.add_error(f"no room '{exit.values['location']}' requested in {exit_name}.location", line)
        if exit.values['target'] not in rooms:
            line = exit_data['target'].number()
            log.info(f"target line: {line}")
            BuildIssueManager.add_error(f"no room '{exit.values['location']}' requested in {exit_name}.target", line)

        return exit

    def parse_item(self, item_name: str, item_data: BlockData) -> python.Object:
        item_varmaps: List[VariableMap] = [
            VariableMap("desc"),
            VariableMap("printed", "printed_name"),
            VariableMap("fixed", expected_type=Config.Type.BOOL),
        ]

        item = python.Object(python.python_name("item", item_name), f"item(\"{item_name}\")")
        map_varmaps(item, item_varmaps, {key: item_data[key].text() for key in item_data})

        if 'pos' in item_data:
            set_pos: python.Call = python.Call("rect.set_pos")
            set_pos.add_arg(python.Value(item_data['pos'].text(), Config.Type.COORD))
            item.add_call(set_pos)
        else:
            in_room = None
            for room in self.get_rooms():
                if item_name in self.get_value('room', room, 'items'):
                    in_room = room
                    break
            if in_room is not None:
                line = list(item_data.values())[0].number()
                BuildIssueManager.add_error(f"Item {item.python_name} has no position defined and is in room {in_room}", line)

        if 'size' in item_data:
            set_size: python.Call = python.Call("rect.set_size")
            set_size.add_arg(python.Value(item_data['size'].text(), Config.Type.COORD))
            item.add_call(set_size)

        return item

    def parse_room(self, room_name: str, room_data: BlockData) -> python.Object:
        room_varmaps: List[VariableMap] = [
            VariableMap("desc"),
            VariableMap("first", "first_desc"),
            VariableMap("printed", "printed_name"),
        ]

        room = python.Object(python.python_name("room", room_name), f"Room(\"{room_name}\")")
        map_varmaps(room, room_varmaps, {key: room_data[key].text() for key in room_data})

        if 'items' in room_data:
            call = python.Call("hotspot_add")
            for item in room_data['items'].text().split(','):
                call.add_arg(python.Value(item, Config.Type.LITERAL))
            room.add_call(call)

        return room

    def parse_item_add_combo(self, combo_name: str, combo_data: BlockData) -> str:
        parts = [n.strip() for n in combo_name.split('+')]
        if len(parts) != 2:
            raise Exception(f"ERROR: incorrect parts in combo '{combo_name}'; expected 2, got {len(parts)}")

        item_name: str = parts[0]
        if not self.has_item(item_name):
            raise Exception(f"ERROR: combo '{combo_name}', no item '{item_name}' defined")
        item_name_python: str = python.python_name('item', item_name)

        target_name: str = parts[1]
        target_name_python: str
        if self.has_item(target_name):
            target_name_python = python.python_name('item', target_name)
        elif self.has_exit(target_name):
            target_name_python = python.python_name('exit', target_name)
        else:
            raise Exception(f"ERROR: for combo, no hotspot target '{target_name}' defined in game configuration")

        python_name = python.python_name('combo', combo_data['name'].text())
        return f"{item_name_python}.add_combination({target_name_python}, {python_name})"

    def write_json(self, game_file_path: Path) -> None:
        import json
        with Path(__file__).parent.joinpath("build", game_file_path).open("w") as file:
            json.dump(self._data, file, indent=4)

    def write_python(self, game_file_path: Path) -> bool:
        script: GameScript = GameScript(Path(__file__).parent.joinpath("build", "bardolf.rpy"), 999, str(game_file_path))

        for item_name, item_data in self._data['item'].items():
            script.add_object(self.parse_item(item_name, item_data))

        for exit_name, exit_data in self._data['exit'].items():
            script.add_object(self.parse_exit(exit_name, exit_data))

        for room_name, room_data in self._data['room'].items():
            script.add_object(self.parse_room(room_name, room_data))

        for combo_name, combo_data in self._data['combo'].items():
            script.add_object(self.parse_combo(combo_name, combo_data))
            script.add_python(self.parse_item_add_combo(combo_name, combo_data))

        if self._start_room is not None:
            start_room = python.python_name("room", self._start_room)
            script.add_return(start_room)

        BuildIssueManager.print()
        if BuildIssueManager.has_error():
            return False
        script.write()
        return True

def get_lines(source_path: Path) -> List[CodeLine]:
    lines: List[CodeLine] = []
    line_number: int = 0
    for line_text in source_path.read_text().splitlines():
        line_number += 1
        line = CodeLine(line_number, line_text)
        line.strip_comment()
        if not line.is_empty():
            lines.append(line)
    log.info(f"Game script loaded with {len(lines)} loc ({line_number} with blank/comments)")
    return lines

def get_blocks(lines: List[CodeLine]) -> List[CodeBlock]:
    current_block: Optional[CodeBlock] = None
    blocks: List[CodeBlock] = []
    indent_errors: List[int] = []
    for line in lines:
        if current_block is not None:
            if line.is_indented():
                current_block.add_line(line)
                continue
            blocks.append(current_block)
            current_block = None
        if line.is_indented():
            indent_errors.append(line.number())
            continue
        current_block = CodeBlock(line.text(), [], line.number())
    log.info(f"{len(blocks)} blocks")
    for block in blocks:
        log.debug(f" -- {block.header()}")
    for line_number in indent_errors:
        BuildIssueManager.add_error("Unexpected indentation", line_number)
    if len(indent_errors) > 0:
        raise Exception("Errors in game source. Cannot proceed.")
    return blocks

def parse_block(block: CodeBlock) -> BlockData:
    log.debug(f"parsing {block.type()} block '{block.name()}'")
    parsed_values: BlockData = {}
    if not block.is_builtin():
        parsed_values['name'] = CodeLine(block.start_line(), str(block.name()))
    multiline = None
    for line in block.lines():
        line_text = line.text()
        if line_text.endswith('\\'):
            if multiline is None:
                multiline = line_text[:-1]
            else:
                multiline += line_text[:-1]
            continue
        if multiline is not None:
            line_text = multiline + line_text
            multiline = None
        if line_text[0].isupper():
            parsed_values['desc'] = CodeLine(line.number(), line_text)
        else:
            parsed_values[line_text.split(' ')[0]] = CodeLine(line.number(), line_text[line_text.index(' ')+1:])
    for key, val in parsed_values.items():
        log.debug(f"|-- {key}: {val}")
    return parsed_values

def parse_block_builtin(blocks: List[CodeBlock], block_type: str) -> BlockData:
    log.info(f"** parsing builtin {block_type}")
    blocks_of_type: List[CodeBlock] = [block for block in blocks if block.type() == block_type]
    if len(blocks_of_type) == 0 or not blocks_of_type[0].is_builtin():
        BuildIssueManager.add_error(f"'{block_type}' is not builtin, or no blocks of that type found")
        return {}
    if len(blocks_of_type) > 1:
        BuildIssueManager.add_error(f"Can only define '{block_type}' once, but it is defined {len(blocks_of_type)} times")
        return {}
    return parse_block(blocks_of_type[0])

def parse_game(blocks: List[CodeBlock]) -> GameData:
    log.info("** parsing blocks")
    game_data: GameData = {'engine': {}}
    for block_type in ['game', 'inventory', 'exits', 'items']:
        game_data['engine'][block_type] = parse_block_builtin(blocks, block_type)
    for block_type in ['combo', 'exit', 'item', 'room']:
        game_data[block_type] = parse_blocks_of_type(blocks, block_type)
    return game_data

def parse_blocks_of_type(blocks: List[CodeBlock], block_type: str) -> SectionData:
    log.info(f"** parsing {block_type}s")
    blocks_of_type: List[CodeBlock] = [block for block in blocks if block.type() == block_type]
    values: SectionData = {}
    block: CodeBlock
    for block in blocks_of_type:
        values[str(block.name())] = parse_block(block)
    return values