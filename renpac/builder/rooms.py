from renpac.base.printv import *

from renpac.builder.Game import *
from renpac.builder.Script import *
from renpac.builder.VariableMap import *

room_varmaps = [
    VariableMap("desc"),
    VariableMap("first", "first_desc"),
    VariableMap("printed", "printed_name")
]

def parse_room(name: str) -> List[str]:
    lines = []

    section_key = f"room.{name}"
    python_name = room_to_python(name)
    lines.append(f"{python_name} = Room(\"{name}\")")

    lines += process_varmaps(room_varmaps, section_key, python_name)

    section = Config.get_section(section_key)
    if not 'items' in section:
        return lines

    for item in section['items'].split(','):
        item = item.strip()
        if not Game.instance().has_hotspot(item):
            printv(f"ERROR: item '{item}' for room '{python_name}' not defined in game configuration")
            continue
        item_python = item_to_python(item)
        lines.append(f"{python_name}.hotspot_add({item_python})")

    return lines

