import logging

from pathlib import Path
from typing import Dict, List, Optional, TypeAlias

from renpac.base import Config
from renpac.base import target

from renpac.builder import issues
from renpac.builder import python

from renpac.builder.GameScript import GameScript
from renpac.builder.VariableMap import VariableMap, map_varmaps

# globals
log = logging.getLogger("renpac")


class CodeLine:
    def __init__(self, number: int, text: str) -> None:
        self._number: int = number
        self._text: str = text.rstrip()

    def __repr__(self) -> str:
        return self._text

    def __str__(self) -> str:
        return self._text

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
        self._name: Optional[str] = None if self.is_builtin(
        ) else self._header[self._header.index(' ')+1:]
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

        self.nventory_anchor: python.Value
        self.inventory_length: python.Value
        self.inventory_depth: python.Value
        self.inventory_items: List[python.Value] = []

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
        self._default_exit_size: python.Value = python.Value(
            self.get_value('engine', 'exits', 'size'), Config.Type.COORD)
        self._default_item_size: python.Value = python.Value(
            self.get_value('engine', 'items', 'size'), Config.Type.COORD)

    def generate_script(self, game_source_path: Path, game_output_path: Path) -> Optional[GameScript]:
        script: GameScript = GameScript(
            game_output_path, 999, str(game_source_path))

        self._objects: Dict[str, Dict[str, python.Object]] = {}

        # create objects
        for type in ['room', 'item', 'combo', 'exit']:
            self._objects[type] = {}
            for name in self._data[type]:
                if type == 'combo':
                    python_name = python.python_name('combo', name)
                    self._objects[type][name] = python.Object(
                        python_name, f"Combination()")
                else:
                    python_name = python.python_name(type, name)
                    self._objects[type][name] = python.Object(
                        python_name, f"{type.title()}(\"{name}\")")

        # set values for objects
        for type, elements_of_type in self._objects.items():
            for name, element_object in elements_of_type.items():
                data = self._data[type][name]
                match type:
                    case 'room': self.parse_room(name, data)
                    case 'item': self.parse_item(name, data)
                    case 'combo': self.parse_combo(name, data)
                    case 'exit': self.parse_exit(name, data)
                script.add_object(element_object)

        for call in self.parse_inventory():
            script.add_call(call)

        if self._start_room is not None:
            start_room = python.python_name("room", self._start_room)
            script.add_return(start_room)

        return None if issues.Manager.has_error() else script

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
            issues.Manager.add_error(
                f"Could not find required {fail} in game data")
        else:
            issues.Manager.add_warning(
                f"Could not find optional {fail} in game data")
        return ""

    def load_game(self) -> None:
        log.info("** loading game definitions")
        self._name = self.get_value('engine', 'game', 'desc')
        log.debug(f"Name: {self._name}")
        self._start_room = self.get_value('engine', 'game', 'start', True)
        log.debug(f"Start room: {self._start_room}")

    def load_inventory(self) -> None:
        valid_anchors: List[str] = ["bottom", "left", "right", "top"]
        anchor_str: str = self.get_value('engine', 'inventory', 'anchor')
        if anchor_str in valid_anchors:
            anchor_str = f"INVENTORY_{anchor_str.upper()}"
            self.inventory_anchor = python.Value(
                anchor_str, Config.Type.LITERAL)
            self.inventory_length = python.Value(self.get_value(
                'engine', 'inventory', 'length'), Config.Type.INT)
            self.inventory_depth = python.Value(self.get_value(
                'engine', 'inventory', 'depth'), Config.Type.INT)
        else:
            log.error(f"illegal inventory anchor '{anchor_str}'")

        items_str: str = self.get_value('game', 'inventory', 'items')
        if items_str != '':
            items: List[str] = items_str.split(',')
            for item_name in items:
                if not self.has_item(item_name):
                    raise Exception(
                        f"ERROR no item '{item_name}' for initial inventory")
                item_python = python.Value(python.python_name(
                    'item', item_name), Config.Type.LITERAL)
                self.inventory_items.append(item_python)

    def get_combo(self, key: str) -> Optional[python.Object]:
        return self._objects['combo'][key] if key in self._objects['combo'] else None

    def get_exit(self, key: str) -> Optional[python.Object]:
        return self._objects['exit'][key] if key in self._objects['exit'] else None

    def get_exits(self) -> List[str]:
        return [exit for exit in self._objects['exit']]

    def get_hotspot(self, key: str) -> Optional[python.Object]:
        exit = self.get_exit(key)
        if exit is None:
            item = self.get_item(key)
            return None if item is None else item
        return exit

    def get_hotspots(self) -> List[str]:
        return self.get_exits() + self.get_hotspots()

    def get_item(self, key: str) -> Optional[python.Object]:
        return self._objects['item'][key] if key in self._objects['item'] else None

    def get_items(self) -> List[str]:
        return [item for item in self._objects['item']]

    def get_room(self, key: str) -> Optional[python.Object]:
        return self._objects['room'][key] if key in self._objects['room'] else None

    def get_rooms(self) -> List[str]:
        return [room for room in self._objects['room']]

    def has_exit(self, exit_name: str) -> bool:
        return exit_name in self.get_exits()

    def has_hotspot(self, hotspot_name: str) -> bool:
        return hotspot_name in self.get_hotspots()

    def has_item(self, item_name: str) -> bool:
        return item_name in self.get_items()

    def has_room(self, room_name: str) -> bool:
        return room_name in self.get_rooms()

    def parse_combo(self, combo_name: str, combo_data: BlockData) -> None:
        combo_varmaps: List[VariableMap] = [
            VariableMap('message'),
            VariableMap('with', 'replace_with'),
        ]

        combo = self.get_combo(combo_name)
        if combo is None:
            raise Exception(f"Combo {combo_name} undefined, cannot parse")
        map_varmaps(combo, combo_varmaps, {
                    key: combo_data[key].text() for key in combo_data})

        if 'with' in combo_data:
            items: List[str] = self.get_items()
            with_name = combo_data['with'].text()
            if with_name not in items:
                issues.Manager.add_error(f"no item '{with_name}' for {combo.python_name}.with",
                                         combo_data['with'].number())

        flags: int = target.TARGET_NONE
        key: str
        for key in ['delete', 'replace']:
            if key in combo_data:
                value = combo_data[key].text()
                if value == 'none':
                    flags = target.TARGET_NONE
                elif value == 'self':
                    flags = target.TARGET_SELF
                elif value == 'other':
                    flags = target.TARGET_OTHER
                elif value == 'both':
                    flags = target.TARGET_SELF | target.TARGET_OTHER
                combo.add_value(key, str(flags), value_type=Config.Type.INT)

        # error checking

        replace: Optional[str] = combo.get_value('replace')
        if replace is not None:
            replace_with: Optional[str] = combo.get_value('replace_with')
            if replace_with is not None and replace == target.TARGET_NONE:
                line = combo_data['replace'].number()
                issues.Manager.add_warning(
                    f"'with' defined in '{combo}' but 'replace' is set to 'none'", line)
            if replace_with is None and replace != target.TARGET_NONE:
                line = combo_data['replace'].number(
                ) if 'replace' in combo_data else -1
                issues.Manager.add_warning(
                    f"'replace' defined in '{combo}' but no 'with' set", line)

        # ignore delete flag if it's the same as replace
        if combo.get_value('delete') == replace:
            combo.values['delete'] = python.Value(
                str(target.TARGET_NONE), Config.Type.INT)

    def parse_exit(self, exit_name: str, exit_data: BlockData) -> None:
        exit_varmaps: List[VariableMap] = [
            VariableMap("message"),
        ]

        exit = self.get_exit(exit_name)
        if exit is None:
            raise Exception(f"exit {exit} undefined, cannot parse")
        map_varmaps(exit, exit_varmaps, {
                    key: exit_data[key].text() for key in exit_data})

        if 'pos' in exit_data:
            set_pos: python.Call = python.Call("rect.set_pos")
            set_pos.add_arg(python.Value(
                exit_data['pos'].text(), Config.Type.COORD))
            exit.add_call(set_pos)
        else:
            issues.Manager.add_error(f"exit {exit.python_name} has no position defined",
                                     list(exit_data.values())[0].number())

        set_size: python.Call = python.Call("rect.set_size")
        size: python.Value = python.Value(exit_data['size'].text(), Config.Type.COORD) \
            if 'size' in exit_data else self._default_exit_size
        set_size.add_arg(size)
        exit.add_call(set_size)

        rooms = self.get_rooms()
        if 'target' in exit_data and exit_data['target'].text() in rooms:
            python_room = python.python_name(
                'room', exit_data['target'].text())
            exit.add_value('target', python_room, Config.Type.LITERAL)

    def parse_item(self, item_name: str, item_data: BlockData) -> None:
        item_varmaps: List[VariableMap] = [
            VariableMap("desc"),
            VariableMap("printed", "printed_name"),
            VariableMap("fixed", expected_type=Config.Type.BOOL),
        ]

        item = self.get_item(item_name)
        if item is None:
            raise Exception(f"item {item} undefined, cannot parse")
        map_varmaps(item, item_varmaps, {
                    key: item_data[key].text() for key in item_data})

        if 'pos' in item_data:
            set_pos: python.Call = python.Call("rect.set_pos")
            set_pos.add_arg(python.Value(
                item_data['pos'].text(), Config.Type.COORD))
            item.add_call(set_pos)
        else:
            in_room = None
            for room in self.get_rooms():
                if '_'.join(item.python_name.split('_')[:-1]) in self.get_value('room', room, 'items'):
                    in_room = room
                    break
            if in_room is not None:
                line = list(item_data.values())[0].number()
                issues.Manager.add_error(
                    f"Item {item.python_name} has no position defined and is in room {in_room}", line)

        set_size: python.Call = python.Call("rect.set_size")
        size: python.Value = python.Value(item_data['size'].text(), Config.Type.COORD) \
            if 'size' in item_data else self._default_item_size
        set_size.add_arg(size)
        item.add_call(set_size)

    def parse_inventory(self) -> List[python.Call]:
        calls: List[python.Call] = []
        set_mode: python.Call = python.Call(
            "Inventory.set_mode", [self.inventory_anchor, self.inventory_length, self.inventory_depth])
        calls.append(set_mode)
        for item in self.inventory_items:
            calls.append(python.Call("Inventory.add", [item]))
        return calls

    def parse_room(self, room_name: str, room_data: BlockData) -> None:
        room_varmaps: List[VariableMap] = [
            VariableMap("desc"),
            VariableMap("first", "first_desc"),
            VariableMap("printed", "printed_name"),
        ]

        room = self.get_room(room_name)
        if room is None:
            raise Exception(f"room {room} undefined, cannot parse")
        map_varmaps(room, room_varmaps, {
                    key: room_data[key].text() for key in room_data})

        if 'exits' in room_data:
            exits: List[str] = self.get_exits()
            for exit in room_data['exits'].text().split(','):
                exit_call: python.Call = python.Call("hotspot_add")
                exit = exit.strip()
                if exit not in exits:
                    issues.Manager.add_error(
                        f"Missing exit {exit} requested for room {room.python_name}")
                exit_call.add_arg(python.Value(
                    python.python_name('exit', exit), Config.Type.LITERAL))
                room.add_call(exit_call)

        if 'items' in room_data:
            items: List[str] = self.get_items()
            for item in room_data['items'].text().split(','):
                item_call: python.Call = python.Call("hotspot_add")
                item = item.strip()
                if item not in items:
                    issues.Manager.add_error(
                        f"Missing item {item} requested for room {room.python_name}")
                item_call.add_arg(python.Value(
                    python.python_name('item', item), Config.Type.LITERAL))
                room.add_call(item_call)

    def parse_item_add_combo(self, combo_name: str) -> str:
        parts = [n.strip() for n in combo_name.split('+')]
        if len(parts) != 2:
            raise Exception(
                f"ERROR: incorrect parts in combo '{combo_name}'; expected 2, got {len(parts)}")

        item_name: str = parts[0]
        if not self.has_item(item_name):
            raise Exception(
                f"ERROR: combo '{combo_name}', no item '{item_name}' defined")
        item_name_python: str = python.python_name('item', item_name)

        target_name: str = parts[1]
        target_name_python: str
        if self.has_item(target_name):
            target_name_python = python.python_name('item', target_name)
        elif self.has_exit(target_name):
            target_name_python = python.python_name('exit', target_name)
        else:
            raise Exception(
                f"ERROR: for combo, no hotspot target '{target_name}' defined in game configuration")

        python_name = python.python_name('combo', combo_name)
        return f"{item_name_python}.add_combination({target_name_python}, {python_name})"

    def validate(self, element_type: str, name_list: List[str], owner_name: str, data: BlockData, key: str):
        room_line: CodeLine = data[key]
        room_name: str = room_line.text()
        if room_name not in name_list:
            issues.Manager.add_error(f"no {element_type} '{room_name}' for {owner_name}.{key}",
                                     room_line.number())

    def validate_exit(self, owner_name: str, data: BlockData, exit_key: str):
        exits: List[str] = self.get_exits()
        self.validate("exit", exits, owner_name, data, exit_key)

    def validate_item(self, owner_name: str, data: BlockData, item_key: str):
        items: List[str] = self.get_items()
        self.validate("item", items, owner_name, data, item_key)

    def validate_room(self, owner_name: str, data: BlockData, room_key: str):
        rooms: List[str] = self.get_rooms()
        self.validate("room", rooms, owner_name, data, room_key)

    def write_json(self, game_file_path: Path) -> None:
        import json
        with Path(__file__).parent.joinpath("build", game_file_path).open("w") as file:
            json.dump(self._data, file, indent=4)


def get_lines(source_path: Path) -> List[CodeLine]:
    lines: List[CodeLine] = []
    line_number: int = 0
    for line_text in source_path.read_text().splitlines():
        line_number += 1
        line = CodeLine(line_number, line_text)
        line.strip_comment()
        if not line.is_empty():
            lines.append(line)
    log.info(
        f"Game script loaded with {len(lines)} loc ({line_number} with blank/comments)")
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
        issues.Manager.add_error("Unexpected indentation", line_number)
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
            parsed_values[line_text.split(' ')[0]] = CodeLine(
                line.number(), line_text[line_text.index(' ')+1:])
    for key, val in parsed_values.items():
        log.debug(f"|-- {key}: {val}")
    return parsed_values


def parse_block_builtin(blocks: List[CodeBlock], block_type: str) -> BlockData:
    log.info(f"** parsing builtin {block_type}")
    blocks_of_type: List[CodeBlock] = [
        block for block in blocks if block.type() == block_type]
    if len(blocks_of_type) == 0 or not blocks_of_type[0].is_builtin():
        issues.Manager.add_error(
            f"'{block_type}' is not builtin, or no blocks of that type found")
        return {}
    if len(blocks_of_type) > 1:
        issues.Manager.add_error(
            f"Can only define '{block_type}' once, but it is defined {len(blocks_of_type)} times")
        return {}
    return parse_block(blocks_of_type[0])


def parse_game(blocks: List[CodeBlock]) -> GameData:
    log.info("** parsing blocks")
    game_data: GameData = {'engine': {}}
    for block_type in ['game', 'inventory', 'exits', 'items']:
        game_data['engine'][block_type] = parse_block_builtin(
            blocks, block_type)
    for block_type in ['combo', 'exit', 'item', 'room']:
        game_data[block_type] = parse_blocks_of_type(blocks, block_type)
    return game_data


def parse_blocks_of_type(blocks: List[CodeBlock], block_type: str) -> SectionData:
    log.info(f"** parsing {block_type}s")
    blocks_of_type: List[CodeBlock] = [
        block for block in blocks if block.type() == block_type]
    values: SectionData = {}
    block: CodeBlock
    for block in blocks_of_type:
        values[str(block.name())] = parse_block(block)
    return values
