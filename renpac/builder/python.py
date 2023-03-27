import string
import re

from typing import Optional
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from renpac.base import Config
from renpac.base import testing

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
    python_key: str
    expected_type: Config.Type
    required: bool = False

room_varmaps: List[VarMap] = [
    VarMap("desc", "desc", Config.Type.STRING),
    VarMap("first", "first_desc", Config.Type.STRING),
    VarMap("printed", "printed_name", Config.Type.STRING),
]

def room_to_python(room_name: str, room_data: Dict[str, str]) -> ScriptObject:
    room = ScriptObject(python_name("room", room_name), f"Room(\"{room_name}\")")

    for varmap in [varmap for varmap in room_varmaps if varmap.renpac_key in room_data]:
        room.add_value(varmap.python_key, room_data[varmap.renpac_key], varmap.expected_type)
    
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
    print(room)

def test_name():
    assert python_name(None, "foo bar") == "foo_bar"
    assert python_name(None, "shebang + bin/bash") == "shebang_bin_bash"
    assert python_name("foo", "bar"),  "foo_bar"
    assert python_name("foo", "shebang + bin/bash"), "foo_shebang_bin_bash"