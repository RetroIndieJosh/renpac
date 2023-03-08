from Game import *
from Script import *
from VariableMap import *

room_varmaps = [
    VariableMap("desc"),
    VariableMap("first", "first_desc"),
    VariableMap("printed", "printed_name")
]

def parse_room(name: str) -> None:
    Script.add_line(f"# ROOM: {name}")

    section_key = f"room.{name}"
    python_name = name_to_python("room", name)
    Script.add_line(f"{python_name} = Room(\"{name}\")")

    process_varmaps(room_varmaps, section_key, python_name)

    parse_hotspots(section_key, "exit", python_name)
    parse_hotspots(section_key, "item", python_name)

def parse_hotspots(section_key: str, type_name: str, python_name: str) -> bool:
    hotspot_key = f"{type_name}s"
    section = Config.get_section(section_key)
    if hotspot_key in section:
        for hotspot in section[hotspot_key].split(','):
            if not Game.has_hotspot(hotspot):
                print(f"ERROR: {type_name} '{hotspot}' for room '{python_name}' does not exist")
            # TODO position (defined in list? or in hotspot definition? how do we get it for this line then?)
            Script.add_line(f"{python_name}.hotspot_add({hotspot.strip().replace(' ', '_')}, 0, 0)")

