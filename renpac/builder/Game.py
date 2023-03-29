import logging

from typing import Dict, List, Optional

from renpac.builder import python

from renpac.builder.RenpyScript import *
from renpac.builder.VariableMap import VariableMap, map_varmaps

# types
BlockData = Dict[str, str]
SectionData = Dict[str, BlockData]
GameData = Dict[str, SectionData]

# globals
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

    def name(self) -> Optional[str]:
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
    def __init__(self, source_path: Path) -> None:
        lines: List[CodeLine] = get_lines(source_path)
        blocks: List[CodeBlock] = get_blocks(lines)
        self._data: GameData = parse_blocks(blocks)

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
                    return block[value_key]
                fail = f"value '{value_key}'"
            else:
                fail = f"block '{block_key}'"
        else:
            fail = f"section '{section_key}'"
        if required:
            log.error(f"Could not find required {fail} in game data")
        else:
            log.warning(f"Could not find optional {fail} in game data")
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

    def get_items(self) -> List[str]:
        return [item for item in self._data['item']]

    def get_rooms(self) -> List[str]:
        return [room for room in self._data['room']]

    def parse_exit(self, exit_name: str, exit_data: Dict[str, str]) -> ScriptObject:
        exit_varmaps: List[VariableMap] = [
            VariableMap("message"),
            VariableMap("location", required=True),
            VariableMap("target", required=True),
        ]

        exit = ScriptObject(python.python_name("exit", exit_name), f"exit(\"{exit_name}\")")
        map_varmaps(exit, exit_varmaps, exit_data)

        if 'pos' in exit_data:
            set_pos: ScriptCall = ScriptCall("rect.set_pos")
            set_pos.add_arg(ScriptValue(exit_data['pos'], Config.Type.COORD))
            exit.add_call(set_pos)
        else:
            log.error(f"exit {exit.name} has no position defined")

        if 'size' in exit_data:
            set_size: ScriptCall = ScriptCall("rect.set_size")
            set_size.add_arg(ScriptValue(exit_data['size'], Config.Type.COORD))
            exit.add_call(set_size)

        rooms = self.get_rooms()
        if exit.values['location'] not in rooms:
            log.error(f"no room '{exit.values['location']}' requested in {exit_name}.location")
        if exit.values['target'] not in rooms:
            log.error(f"no room '{exit.values['location']}' requested in {exit_name}.target")

        return exit

    def parse_item(self, item_name: str, item_data: Dict[str, str]) -> ScriptObject:
        item_varmaps: List[VariableMap] = [
            VariableMap("desc"),
            VariableMap("printed", "printed_name"),
            VariableMap("fixed", expected_type=Config.Type.BOOL),
        ]

        item = ScriptObject(python.python_name("item", item_name), f"item(\"{item_name}\")")
        map_varmaps(item, item_varmaps, item_data)

        if 'pos' in item_data:
            set_pos: ScriptCall = ScriptCall("rect.set_pos")
            set_pos.add_arg(ScriptValue(item_data['pos'], Config.Type.COORD))
            item.add_call(set_pos)
        else:
            in_room = None
            for room in self.get_rooms():
                if item_name in self.get_value('room', room, 'items'):
                    in_room = room
                    break
            if in_room is not None:
                log.error(f"Item {item.name} has no position defined and is in room {in_room}")

        if 'size' in item_data:
            set_size: ScriptCall = ScriptCall("rect.set_size")
            set_size.add_arg(ScriptValue(item_data['size'], Config.Type.COORD))
            item.add_call(set_size)

        return item

    def parse_room(self, room_name: str, room_data: Dict[str, str]) -> ScriptObject:
        room_varmaps: List[VariableMap] = [
            VariableMap("desc"),
            VariableMap("first", "first_desc"),
            VariableMap("printed", "printed_name"),
        ]

        room = ScriptObject(python.python_name("room", room_name), f"Room(\"{room_name}\")")
        map_varmaps(room, room_varmaps, room_data)

        if 'items' in room_data:
            call = ScriptCall("hotspot_add")
            for item in room_data['items'].split(','):
                call.add_arg(ScriptValue(item, Config.Type.LITERAL))
            room.add_call(call)

        return room

    def write_json(self, game_file_path: Path) -> None:
        import json
        with Path(__file__).parent.joinpath("build", game_file_path).open("w") as file:
            json.dump(self._data, file, indent=4)

    def write_python(self, game_file_path: Path):
        script: GameScript = GameScript(Path(__file__).parent.joinpath("build", "bardolf.rpy"), 999, str(game_file_path))
        for combo, data in self._data['combo'].items():
            script.add_python("# " + python.python_name("combo", combo.replace('+', 'and')))
        for exit, data in self._data['exit'].items():
            script.add_object(self.parse_exit(exit, data))
        for item, data in self._data['item'].items():
            script.add_object(self.parse_item(item, data))
        for room, data in self._data['room'].items():
            script.add_object(self.parse_room(room, data))

        if self._start_room is not None:
            start_room = python.python_name("room", self._start_room)
            script.add_return(start_room)

        script.write()

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
    errors: List[str] = []
    for line in lines:
        if current_block is not None:
            if line.is_indented():
                current_block.add_line(line.text().lstrip())
                continue
            blocks.append(current_block)
            current_block = None
        if line.is_indented():
            errors.append(f"[{line.number()}] Unexpected indentation")
            continue
        current_block = CodeBlock(line.text(), [])
    log.info(f"{len(blocks)} blocks")
    for block in blocks:
        log.debug(f" -- {block.header()}")
    for error in errors:
        log.error(error)
    if len(errors) > 0:
        raise Exception("Errors in game source. Cannot proceed.")
    return blocks

def parse_block(block: CodeBlock) -> BlockData:
    log.debug(f"parsing {block.type()} block '{block.name()}'")
    parsed_values: BlockData = {}
    if not block.is_builtin():
        parsed_values['name'] = str(block.name())
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

def parse_block_builtin(blocks: List[CodeBlock], block_type: str) -> BlockData:
    log.info(f"** parsing builtin {block_type}")
    blocks_of_type: List[CodeBlock] = [block for block in blocks if block.type() == block_type]
    if len(blocks_of_type) == 0 or not blocks_of_type[0].is_builtin():
        log.error(f"'{block_type}' is not builtin, or no blocks of that type found")
        return {}
    if len(blocks_of_type) > 1:
        log.error(f"Can only define '{block_type}' once, but it is defined {len(blocks_of_type)} times.")
        return {}
    return parse_block(blocks_of_type[0])

def parse_blocks(blocks: List[CodeBlock]) -> GameData:
    log.info("** parsing blocks")
    parsed_blocks: Dict[str, Dict[str, Dict[str, str]]] = {'engine': {}}
    for block_type in ['game', 'inventory', 'exits', 'items']:
        parsed_blocks['engine'][block_type] = parse_block_builtin(blocks, block_type)
    for block_type in ['combo', 'exit', 'item', 'room']:
        parsed_blocks[block_type] = parse_blocks_of_type(blocks, block_type)
    return parsed_blocks

def parse_blocks_of_type(blocks: List[CodeBlock], block_type: str) -> SectionData:
    log.info(f"** parsing {block_type}s")
    blocks_of_type: List[CodeBlock] = [block for block in blocks if block.type() == block_type]
    values: SectionData = {}
    block: CodeBlock
    for block in blocks_of_type:
        values[str(block.name())] = parse_block(block)
    return values