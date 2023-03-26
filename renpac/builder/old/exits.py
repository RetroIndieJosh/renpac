import logging

from renpac.builder import python

from renpac.builder.Game import *
from renpac.builder.VariableMap import *

log = logging.getLogger("exit")

def parse_exit(exit_name: str) -> List[str]:
    exit_varmaps: List[VariableMap] = [
        VariableMap("message"),
        VariableMap("pos", config_type=Type.COORD),
        VariableMap("size", config_type=Type.SIZE, fallback=Game.instance().default_exit_size())
    ]

    lines: List[str] = []

    section_key: str = f"exit.{exit_name}"
    python_name: str = python.exit(exit_name)
    lines.append(f"{python_name} = Exit(\"{exit_name}\")")

    section: SectionProxy = Game.instance().config().get_section(section_key)
    if 'location' in section:
        location: str = section['location']
        if Game.instance().has_room(location):
            location_python: str = python.room(location)
            lines.append(f"{location_python}.hotspot_add({python_name})")
        else:
            log.warning(f"no room {location} for 'location' of {section_key}")
    if 'target' in section:
        target: str = section['target']
        if Game.instance().has_room(target):
            target_python: str = python.room(target)
            lines.append(f"{python_name}.target = {target_python}")
        else:
            log.warning(f"no room {target} for 'target' of {section_key}")

    lines += process_varmaps(Game.instance().config(), exit_varmaps, section_key, python_name)

    return lines