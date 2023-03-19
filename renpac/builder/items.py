from renpac.builder import python

from renpac.builder.Game import Game
from renpac.builder.VariableMap import *

def parse_item(item_name: str) -> List[str]:
    item_varmaps = [
        VariableMap("desc"),
        VariableMap("printed", "printed_name"),
        VariableMap("fixed", type=ConfigType.BOOL),
        VariableMap("pos", type=ConfigType.POSITION),
        VariableMap("size", type=ConfigType.SIZE, default=Game.instance().default_item_size())
    ]

    lines = []

    config_key = f"item.{item_name}"
    python_name = python.item(item_name)
    lines.append(f"{python_name} = Item(\"{item_name}\")")

    lines += process_varmaps(Game.instance().config(), item_varmaps, config_key, python_name)

    return lines
