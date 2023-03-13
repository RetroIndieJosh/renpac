import platform
import shutil
import subprocess

from combos import *
from exits import *
from items import *
from rooms import *

from Config import Config
from Game import Game
from Script import Script

GAME_NAME = "bardolf"

FILE_PATH = os.path.dirname(__file__)

GAME_CONFIG = f"{FILE_PATH}/../{GAME_NAME}.cfg"
ENGINE_PATH = f"{FILE_PATH}/../renpac-engine"

OUTPUT_PATH = f"{FILE_PATH}/build//{GAME_NAME}/game"
GAME_FILE_PATH = f"{OUTPUT_PATH}/{GAME_NAME}.game.rpy"

def build_game() -> None:
    Config.load(GAME_CONFIG)

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

    print(f"writing game file to '{GAME_FILE_PATH}'")
    Script.write_file(GAME_FILE_PATH)

def build_engine() -> None:
    if platform.system() == "Windows":
        builder = "generate.bat"
    else:
        builder = "generate.sh"

    os.chdir(ENGINE_PATH)

    print(f"building engine: {builder}")
    subprocess.run(builder)

    os.chdir(os.path.dirname(__file__))

def clean() -> None:
    shutil.rmtree(OUTPUT_PATH, ignore_errors=True)

def copy_engine() -> None:
    print(f"copying engine to '{OUTPUT_PATH}'")
    # TODO if building for release, include .rpyc and but exclude .rpy
    shutil.copytree(f"{ENGINE_PATH}/game", OUTPUT_PATH, 
                    ignore=shutil.ignore_patterns("renpac-engine", "*.py", "*.pyc", "*.rpyc", "*.bak"),
                    copy_function=shutil.copy2)

def main() -> None:
    clean()
    build_engine()
    copy_engine()
    build_game()

if __name__ == "__main__":
    main()