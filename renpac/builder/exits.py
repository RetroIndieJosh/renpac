from renpac.base.printv import *

from renpac.builder import python

from renpac.builder.Game import *
from renpac.builder.VariableMap import *

def parse_exit(exit_name: str) -> List[str]:
    exit_varmaps = [
        VariableMap("message"),
        VariableMap("pos", type=ConfigType.POSITION),
        VariableMap("size", type=ConfigType.SIZE, default=Game.instance().default_exit_size())
    ]

    lines = []

    section_key = f"exit.{exit_name}"
    python_name = python.exit(exit_name)
    lines.append(f"{python_name} = Exit(\"{exit_name}\")")

    section = Game.instance().config().get_section(section_key)
    if 'location' in section:
        location = section['location']
        if Game.instance().has_room(location):
            location_python = python.room(location)
            lines.append(f"{location_python}.hotspot_add({python_name})")
        else:
            printv(f"WARN no room {location} for 'location' of {section_key}")
    if 'target' in section:
        target = section['target']
        if Game.instance().has_room(target):
            target_python = python.room(target)
            lines.append(f"{python_name}.target = {target_python}")
        else:
            printv(f"WARN no room {target} for 'target' of {section_key}")

    lines += process_varmaps(Game.instance().config(), exit_varmaps, section_key, python_name)

    return lines