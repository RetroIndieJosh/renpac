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

Game.parse_definitions()
Game.report_definitions()

# TODO major problem: exits reference rooms for their target location, but rooms reference exits to add as hotspots!

# do exits and items first since rooms and combos can reference them
Game.all_exits(parse_exit)
Game.all_items(parse_item)

Game.all_rooms(parse_room)
Game.all_combos(parse_combo)

Game.parse_game()
Game.parse_inventory()

Game.finalize()

print("\n\n***SCRIPT BEGIN***\n")
Script.print()
print("\n\n***SCRIPT END***\n")

print(f"writing file to '{OUTPUT_PATH}'")
Script.write_file(OUTPUT_PATH)