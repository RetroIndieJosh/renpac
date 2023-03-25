import logging

from renpac.builder import python

from renpac.builder.Game import *
from renpac.builder.Script import *
from renpac.builder.VariableMap import *

log = logging.getLogger("rooms")

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

    lines += process_varmaps(Game.instance().config(), room_varmaps, section_key, python_name)

    section = Game.instance().config().get_section(section_key)
    if not 'items' in section:
        return lines

    for item_name in section['items'].split(','):
        item_name = item_name.strip()
        if not Game.instance().has_hotspot(item_name):
            log.error(f"item '{item_name}' for room '{python_name}' not defined in game configuration")
            continue
        item_python = python.item(item_name)
        lines.append(f"{python_name}.hotspot_add({item_python})")

    return lines

