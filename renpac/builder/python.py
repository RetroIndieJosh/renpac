import logging
import string
import re

from typing import Optional
from typing import Dict, List, Optional

from renpac.base import Config

from renpac.builder.RenpyScript import ScriptCall, ScriptObject, ScriptValue
from renpac.builder.VariableMap import VarMap, map_varmaps

log = logging.getLogger("python")

def python_name(type: Optional[str], n: str) -> str:
    n = n.strip()
    chars = re.escape(string.punctuation + string.whitespace)
    n = re.sub('['+chars+']', '_', n)
    while "__" in n:
        n = n.replace("__", "_")
    if type is None:
        return n
    return f"{type}_{n}"

item_varmaps: List[VarMap] = [
    VarMap("desc"),
    VarMap("printed", "printed_name"),
    VarMap("fixed", expected_type=Config.Type.BOOL),
]

room_varmaps: List[VarMap] = [
    VarMap("desc"),
    VarMap("first", "first_desc"),
    VarMap("printed", "printed_name"),
]

def parse_item(item_name: str, item_data: Dict[str, str]) -> ScriptObject:
    item = ScriptObject(python_name("item", item_name), f"item(\"{item_name}\")")
    map_varmaps(item, item_varmaps, item_data)

    if 'pos' in item_data:
        set_pos: ScriptCall = ScriptCall("rect.set_pos")
        set_pos.add_arg(ScriptValue(item_data['pos'], Config.Type.COORD))
        item.add_call(set_pos)
    else:
        # TODO only if not in 'nowhere' (need to leave through rooms to determine)
        log.error(f"Item {item.name} has no position defined")

    if 'size' in item_data:
        set_size: ScriptCall = ScriptCall("rect.set_size")
        set_size.add_arg(ScriptValue(item_data['size'], Config.Type.COORD))
        item.add_call(set_size)

    return item

def parse_room(room_name: str, room_data: Dict[str, str]) -> ScriptObject:
    room = ScriptObject(python_name("room", room_name), f"Room(\"{room_name}\")")
    map_varmaps(room, room_varmaps, room_data)
    
    if 'items' in room_data:
        call = ScriptCall("hotspot_add")
        for item in room_data['items'].split(','):
            call.add_arg(ScriptValue(item, Config.Type.LITERAL))
        room.add_call(call)

    return room

def test_item():
    data = {
        'desc': "A test item.",
        'printed': "Test Item",
        'fixed': False,
        'pos': "98 14",
        'size': "100 150",
    }
    item = parse_item("test_item", data)

    for key in ['desc', 'printed']:
        assert item.values[key].value == data[key]
        assert item.values[key].expected_type == Config.Type.STRING

    assert item.values['fixed'].value == False
    assert item.values['fixed'].expected_type == Config.Type.BOOL

    assert item.calls[0].func == "rect.set_pos"
    assert len(item.calls[0].args) == 1
    assert item.calls[0].args[0].to_python() == '*(98, 14)'
    assert item.calls[0].args[0].expected_type == Config.Type.COORD

    assert item.calls[1].func == "rect.set_size"
    assert len(item.calls[0].args) == 1
    assert item.calls[1].args[0].to_python() == '*(100, 150)'
    assert item.calls[1].args[0].expected_type == Config.Type.COORD

def test_name():
    assert python_name(None, "foo bar") == "foo_bar"
    assert python_name(None, "shebang + bin/bash") == "shebang_bin_bash"
    assert python_name("foo", "bar") ==  "foo_bar"
    assert python_name("foo", "shebang + bin/bash") == "foo_shebang_bin_bash"

def test_room():
    data = {
        'desc': "A test room.",
        'first': "You enter for the first time.",
        'printed': "Test Room",
        'items': "coin, dagger, bottle, bag",
    }
    room = parse_room("test_room", data)

    for key in ['desc', 'first', 'printed']:
        assert room.values[key].value == data[key]
        assert room.values[key].expected_type == Config.Type.STRING

    assert room.calls[0].func == "hotspot_add"
    assert len(room.calls[0].args) == 4

    print(room.calls[0].args)

    assert room.calls[0].args[0].to_python() == 'coin'
    assert room.calls[0].args[0].expected_type == Config.Type.LITERAL
    assert room.calls[0].args[1].to_python() == 'dagger'
    assert room.calls[0].args[1].expected_type == Config.Type.LITERAL
    assert room.calls[0].args[2].to_python() == 'bottle'
    assert room.calls[0].args[2].expected_type == Config.Type.LITERAL
    assert room.calls[0].args[3].to_python() == 'bag'
    assert room.calls[0].args[3].expected_type == Config.Type.LITERAL
