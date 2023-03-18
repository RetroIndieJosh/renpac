from renpac.base.printv import *

from renpac.builder.Game import *
from renpac.builder.VariableMap import *

exit_varmaps = [
    VariableMap("message"),
    VariableMap("pos", type=TYPE_POSITION),
    VariableMap("size", type=TYPE_SIZE)
]

def parse_exit(name: str) -> None:
    Script.add_header(f"EXIT: {name}")

    section_key = f"exit.{name}"
    python_name = name_to_python("exit", name)
    Script.add_line(f"{python_name} = Exit(\"{name}\")")

    section = Config.get_section(section_key)
    if 'location' in section:
        location = section['location']
        if Game.has_room(location):
            location_python = name_to_python("room", location)
            Script.add_line(f"{location_python}.hotspot_add({python_name})")
        else:
            printv(f"WARN no room {location} for 'location' of {section_key}")
    if 'target' in section:
        target = section['target']
        if Game.has_room(target):
            target_python = name_to_python("room", target)
            Script.add_line(f"{python_name}.target = {target_python}")
        else:
            printv(f"WARN no room {target} for 'target' of {section_key}")

    process_varmaps(exit_varmaps, section_key, python_name)