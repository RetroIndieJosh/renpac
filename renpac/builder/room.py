from typing import Callable, Dict, List, Optional, Tuple

from renpac.builder import python

from renpac.builder.RenpyScript import ScriptObject
from renpac.builder.VariableMap import VariableMap, process_varmaps

room_varmaps = {
    "desc": "desc",
    "first": "first_desc",
    "printed": "printed_name",
}

def room_to_python(room_name: str, room_data: Dict[str, str]) -> ScriptObject:
    python_name = python.room(room_name)
    init = f"{python_name} = Room(\"{room_name}\")"
    room = ScriptObject(python_name, init)
    for renpac_key in [var for var in room_varmaps if var in room_data]:
        python_key = room_varmaps[renpac_key]
        room.add_value(python_key, room_data[renpac_key])
    return room

if __name__ == "__main__":
    print("no tests")