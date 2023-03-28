import string
import re

from typing import Optional
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from renpac.base import Config

from renpac.builder.RenpyScript import ScriptCall, ScriptObject, ScriptValue
from renpac.builder.VariableMap import VariableMap, process_varmaps

def python_name(type: Optional[str], n: str) -> str:
    n = n.strip()
    chars = re.escape(string.punctuation + string.whitespace)
    n = re.sub('['+chars+']', '_', n)
    while "__" in n:
        n = n.replace("__", "_")
    if type is None:
        return n
    return f"{type}_{n}"

@dataclass(frozen = True)
class VarMap:
    renpac_key: str
    python_key: Optional[str] = None
    expected_type: Config.Type = Config.Type.STRING
    required: bool = False

item_varmaps: List[VarMap] = [
    VarMap("desc"),
    VarMap("printed", "printed_name"),
    VarMap("fixed", expected_type=Config.Type.BOOL),
    VarMap("pos", expected_type=Config.Type.COORD),
    VarMap("size", expected_type=Config.Type.COORD),
]

room_varmaps: List[VarMap] = [
    VarMap("desc"),
    VarMap("first", "first_desc"),
    VarMap("printed", "printed_name"),
]

def map_varmaps(obj: ScriptObject, varmaps: List[VarMap], data: Dict[str, str]):
    for varmap in [varmap for varmap in varmaps if varmap.renpac_key in data]:
        python_key: str = varmap.renpac_key if varmap.python_key is None else varmap.renpac_key
        obj.add_value(python_key, data[varmap.renpac_key], varmap.expected_type)

def room_to_python(room_name: str, room_data: Dict[str, str]) -> ScriptObject:
    room = ScriptObject(python_name("room", room_name), f"Room(\"{room_name}\")")
    map_varmaps(room, room_varmaps, room_data)
    
    if 'items' in room_data:
        call = ScriptCall("hotspot_add")
        for item in room_data['items'].split(','):
            call.add_arg(ScriptValue(item, Config.Type.LITERAL))
        room.add_call(call)

    return room

def test_room():
    data = {
        "desc": "A test room.",
        "first": "You enter for the first time.",
        "printed": "Test Room",
        "items": "coin, dagger, bottle, bag",
    }
    room = room_to_python("test_room", data)

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

def test_name():
    assert python_name(None, "foo bar") == "foo_bar"
    assert python_name(None, "shebang + bin/bash") == "shebang_bin_bash"
    assert python_name("foo", "bar") ==  "foo_bar"
    assert python_name("foo", "shebang + bin/bash") == "foo_shebang_bin_bash"