from renpac.base.printv import *

from renpac.builder.Game import *
from renpac.builder.VariableMap import *

def parse_exit(name: str) -> list[str]:
    exit_varmaps = [
        VariableMap("message"),
        VariableMap("pos", type=TYPE_POSITION),
        VariableMap("size", type=TYPE_SIZE, default=Game.instance().default_exit_size())
    ]

    lines = []

    section_key = f"exit.{name}"
    python_name = exit_to_python(name)
    lines.append(f"{python_name} = Exit(\"{name}\")")

    section = Config.get_section(section_key)
    if 'location' in section:
        location = section['location']
        if Game.instance().has_room(location):
            location_python = room_to_python(location)
            lines.append(f"{location_python}.hotspot_add({python_name})")
        else:
            printv(f"WARN no room {location} for 'location' of {section_key}")
    if 'target' in section:
        target = section['target']
        if Game.instance().has_room(target):
            target_python = room_to_python(target)
            lines.append(f"{python_name}.target = {target_python}")
        else:
            printv(f"WARN no room {target} for 'target' of {section_key}")

    lines += process_varmaps(exit_varmaps, section_key, python_name)

    return lines