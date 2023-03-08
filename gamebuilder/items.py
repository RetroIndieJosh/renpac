from VariableMap import *

item_varmaps = [
    VariableMap("desc"),
    VariableMap("printed", "printed_name"),
    VariableMap("fixed", type=TYPE_BOOL)
]

def parse_item(name: str) -> None:
    Script.add_line(f"# ITEM: {name}")

    config_key = f"item.{name}"
    python_name = name.replace(' ', '_')
    Script.add_line(f"{python_name} = Item(\"{name}\")")

    process_varmaps(item_varmaps, config_key, python_name)
