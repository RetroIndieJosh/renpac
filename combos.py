from printv import *

from Game import *
from VariableMap import *

TARGET_NONE = 0b00
TARGET_SELF = 0b01
TARGET_OTHER = 0b10

def parse_combo(section_key: str) -> None:
    parts = section_key.split('+')
    if len(parts) > 2:
        printv("ERROR: too many parts in combo '{combo}'")
        return

    item = parts[0].split('.')[1].strip()
    target = parts[1].split('.')[1].strip()
    if not Game.has_item(item):
        printv(f"ERROR: for combo, no item '{item}' defined in game configuration")
    if not Game.has_hotspot(target):
        printv(f"ERROR: for combo, no hotspot target '{target}' defined in game configuration")

    # reuse parts here so we keep the prefix (item. => item_ or exit. => exit_)
    item_python = parts[0].strip().replace('.', '_').replace(' ', '_')
    target_python = parts[1].strip().replace('.', '_').replace(' ', '_')
    Script.add_header(f"COMBO: {item_python} + {target_python}")

    message = None
    delete_flags = "TARGET_NONE"
    replace_flags = "TARGET_NONE"
    replace_with = None

    section = Config.get_section(section_key)

    # TODO change to a loop to catch repeats and illegal keys
    # TODO these could probably be done with varmaps? at least message

    if 'delete' in section:
        delete_target = section['delete']
        if delete_target == 'none':
            delete_flags = "TARGET_NONE"
        elif delete_target == 'self':
            delete_flags = "TARGET_SELF"
        elif delete_target == 'other':
            delete_flags = "TARGET_OTHER"
        elif delete_target == 'both':
            delete_flags = "TARGET_SELF | TARGET_OTHER"

    if 'message' in section:
        message = section['message']
    
    if 'replace' in section:
        replace_target = section['replace']
        if replace_target == 'none':
            replace_flags = "TARGET_NONE"
        elif replace_target == 'self':
            replace_flags = "TARGET_SELF"
        elif replace_target == 'other':
            replace_flags = "TARGET_OTHER"
        elif replace_target == 'both':
            printv("ERROR: 'both' is not valid for 'replace' in combo")
        else:
            printv(f"ERROR: unknown value for 'replace' in combo: {replace_target}")
    
    if 'with' in section:
        replace_with = name_to_python("item", section['with'])

    # error checking

    if replace_with is not None and replace_flags == "TARGET_NONE":
        printv(f"WARN: 'with' defined in '{section_key}' but 'replace' is set to 'none'")

    if replace_with is None and replace_flags != "TARGET_NONE":
        printv(f"WARN: 'replace' defined in '{section_key}' but no 'with' set")

    # ignore delete flag if it's the same as replace
    if replace_flags == delete_flags:
        delete_flags = "TARGET_NONE"

    if message is None:
        printv(f"WARN: no message for combo '{section_key}")

    python_name = name_to_python("combo", section_key).replace('.', '_').replace('+', 'plus')
    Script.add_line(f"{python_name} = Combination(\"{message}\", {delete_flags}, {replace_flags}, {replace_with})")
    Script.add_line(f"{item_python}.add_combination({target_python}, {python_name})")