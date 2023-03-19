from renpac.base.printv import *

from renpac.builder import python

from renpac.builder.Game import *
from renpac.builder.VariableMap import *

TARGET_NONE = 0b00
TARGET_SELF = 0b01
TARGET_OTHER = 0b10

def parse_combo(section_key: str) -> List[str]:
    parts = section_key.split('+')
    if len(parts) > 2:
        printv("ERROR: too many parts in combo '{combo}'")
        return

    item_name = parts[0].split('.')[1].strip()
    target_name = parts[1].split('.')[1].strip()

    if not Game.instance().has_item(item_name):
        printv(f"ERROR: for combo, no item '{item_name}' defined in game configuration")
    if not Game.instance().has_hotspot(target_name):
        printv(f"ERROR: for combo, no hotspot target '{target_name}' defined in game configuration")

    # reuse parts here so we keep the prefix (item. => item_ or exit. => exit_)
    item_python = python.name(None, parts[0])
    target_python = python.name(None, parts[1])

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
        replace_with = python.item(section['with'])

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

    python_name = python.combo(section_key).replace('.', '_').replace('+', 'plus')

    return [
        f"{python_name} = Combination(\"{message}\", {delete_flags}, {replace_flags}, {replace_with})",
        f"{item_python}.add_combination({target_python}, {python_name})"]