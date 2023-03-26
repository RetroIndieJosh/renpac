from renpac.builder import python

from renpac.builder.Game import Game
from renpac.builder.VariableMap import *

def parse_item(item_name: str) -> List[str]:
    item_varmaps: List[VariableMap] = [
        VariableMap("desc"),
        VariableMap("printed", "printed_name"),
        VariableMap("fixed", config_type=Type.BOOL),
        VariableMap("pos", config_type=Type.COORD),
        VariableMap("size", config_type=Type.SIZE, fallback=Game.instance().default_item_size())
    ]

    lines: List[str]  = []

    config_key: str = f"item.{item_name}"
    python_name: str = python.item(item_name)
    lines.append(f"{python_name} = Item(\"{item_name}\")")

    lines += process_varmaps(Game.instance().config(), item_varmaps, config_key, python_name)

    return lines
