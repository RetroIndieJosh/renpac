from Game import *
from Script import *
from VariableMap import *

room_varmaps = [
    VariableMap("desc"),
    VariableMap("first", "first_desc"),
    VariableMap("printed", "printed_name")
]

def parse_room(name: str) -> None:
    Script.add_header(f"ROOM: {name}")

    section_key = f"room.{name}"
    python_name = name_to_python("room", name)
    Script.add_line(f"{python_name} = Room(\"{name}\")")

    process_varmaps(room_varmaps, section_key, python_name)

    section = Config.get_section(section_key)
    if not 'items' in section:
        return

    for item in section['items'].split(','):
        if not Game.has_hotspot(item):
            print(f"ERROR: item '{item}' for room '{python_name}' not defined in game configuration")
        item_python = name_to_python("item", item)
        Script.add_line(f"{python_name}.hotspot_add({item_python})")

