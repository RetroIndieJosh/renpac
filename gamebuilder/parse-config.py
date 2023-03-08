from combos import *
from exits import *
from items import *
from rooms import *

from Config import *
from Game import *
from Script import *
from VariableMap import *

GAME_NAME = "bardolf"
CONFIG_FILE = f"gameconfigs/{GAME_NAME}.cfg"
OUTPUT_PATH = f"game/{GAME_NAME}.game.rpy"

Config.load(CONFIG_FILE)

# gather a lits of elements in the script so it doesn't need to be in order
Game.parse_definitions()
Game.report_definitions()

# must be in order items, rooms, exits, combos
Game.all_items(parse_item)

# rooms list items contained in them
Game.all_rooms(parse_room)

# exits define their room location and target
Game.all_exits(parse_exit)

# combos can refer to both items and exits
Game.all_combos(parse_combo)

Game.parse_game()
Game.parse_inventory()

Game.finalize()

print("\n\n***SCRIPT BEGIN***\n")
Script.print()
print("\n\n***SCRIPT END***\n")

print(f"writing file to '{OUTPUT_PATH}'")
Script.write_file(OUTPUT_PATH)