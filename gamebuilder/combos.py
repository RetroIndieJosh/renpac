from VariableMap import *

TARGET_NONE = 0b00
TARGET_SELF = 0b01
TARGET_OTHER = 0b10

def parse_combo(section_key: str) -> None:
    parts = section_key.split('+')
    if len(parts) > 2:
        print("ERROR: too many parts in combo '{combo}'")
        return

    item = parts[0].strip().replace('.', '_').replace(' ', '_')
    target = parts[1].strip().replace('.', '_').replace(' ', '_')
    Script.add_line(f"# COMBO: {item} + {target}")

    message = None
    delete_flags = TARGET_NONE
    replace_flags = TARGET_NONE
    replace_with = None

    section = Config.get_section(section_key)

    # TODO change to a loop to catch repeats and illegal keys

    if 'delete' in section:
        delete_target = section['delete']
        if delete_target == 'none':
            delete_flags = TARGET_NONE
        elif delete_target == 'none':
            delete_flags = TARGET_NONE
        elif delete_target == 'none':
            delete_flags = TARGET_NONE
        elif delete_target == 'both':
            delete_flags = TARGET_SELF | TARGET_OTHER

    if 'message' in section:
        message = section['message']
    
    if 'replace' in section:
        replace_target = section['replace']
        if replace_target == 'none':
            replace_flags = TARGET_NONE
        elif replace_target == 'none':
            replace_flags = TARGET_NONE
        elif replace_target == 'none':
            replace_flags = TARGET_NONE
        elif replace_target == 'both':
            print("ERROR: 'both' is not valid for 'replace' in combo")
        else:
            print(f"ERROR: unknown value for 'replace' in combo: {replace_target}")
    
    if 'with' in section:
        replace_with = name_to_python("item", section['with'])

    if replace_with is not None and replace_flags == TARGET_NONE:
        print(f"WARN: 'with' defined in '{section_key}' but 'replace' is set to 'none'")

    if replace_with is None and replace_flags != TARGET_NONE:
        print(f"WARN: 'replace' defined in '{section_key}' but no 'with' set")

    if message is None:
        print(f"WARN: no message for combo '{section_key}")

    python_name = name_to_python("combo", section_key).replace('.', '_').replace('+', 'plus')
    Script.add_line(f"{python_name} = Combination(\"{message}\", {delete_flags}, {replace_flags}, {replace_with})")