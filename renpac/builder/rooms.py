from renpac.base.printv import *

from renpac.builder import python

from renpac.builder.Game import *
from renpac.builder.Script import *
from renpac.builder.VariableMap import *

room_varmaps = [
    VariableMap("desc"),
    VariableMap("first", "first_desc"),
    VariableMap("printed", "printed_name")
]

def parse_room(room_name: str) -> List[str]:
    lines = []

    section_key = f"room.{room_name}"
    python_name = python.room(room_name)
    lines.append(f"{python_name} = Room(\"{room_name}\")")

    lines += process_varmaps(room_varmaps, section_key, python_name)

    section = Config.get_section(section_key)
    if not 'items' in section:
        return lines

    for item_name in section['items'].split(','):
        item_name = item_name.strip()
        if not Game.instance().has_hotspot(item_name):
            printv(f"ERROR: item '{item_name}' for room '{python_name}' not defined in game configuration")
            continue
        item_python = python.item(item_name)
        lines.append(f"{python_name}.hotspot_add({item_python})")

    return lines

