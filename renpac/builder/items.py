from renpac.builder.VariableMap import *

item_varmaps = [
    VariableMap("desc"),
    VariableMap("printed", "printed_name"),
    VariableMap("fixed", type=TYPE_BOOL),
    VariableMap("pos", type=TYPE_POSITION),
    VariableMap("size", type=TYPE_SIZE)
]

def parse_item(name: str) -> None:
    Script.add_header(f"ITEM: {name}")

    config_key = f"item.{name}"
    python_name = name_to_python("item", name)
    Script.add_line(f"{python_name} = Item(\"{name}\")")

    process_varmaps(item_varmaps, config_key, python_name)
