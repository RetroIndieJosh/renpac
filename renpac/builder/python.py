import logging
import string
import re

from typing import Optional
from typing import Dict, List, Optional

from renpac.base import Config

from renpac.builder.RenpyScript import ScriptCall, ScriptObject, ScriptValue
from renpac.builder.VariableMap import VariableMap, map_varmaps

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
