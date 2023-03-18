from renpac.builder.VariableMap import *

item_varmaps = [
    VariableMap("desc"),
    VariableMap("printed", "printed_name"),
    VariableMap("fixed", type=TYPE_BOOL),
    VariableMap("pos", type=TYPE_POSITION),
    VariableMap("size", type=TYPE_SIZE)
]

def parse_item(name: str) -> list[str]:
    lines = []

    config_key = f"item.{name}"
    python_name = name_to_python("item", name)
    lines.append(f"{python_name} = Item(\"{name}\")")

    lines += process_varmaps(item_varmaps, config_key, python_name)

    return lines
