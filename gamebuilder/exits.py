from Game import *
from VariableMap import *

exit_varmaps = [
]

def parse_exit(name: str) -> None:
    Script.add_line(f"# EXIT: {name}")

    section_key = f"exit.{name}"
    python_name = name_to_python("exit", name)
    Script.add_line(f"{python_name} = Exit(\"{name}\")")

    section = Config.get_section(section_key)
    if 'location' in section:
        location = section['location']
        if Game.has_room(location):
            location_python = name_to_python("room", location)
            Script.add_line(f"{location_python}.hotspot_add({python_name})")

    process_varmaps(exit_varmaps, section_key, python_name)