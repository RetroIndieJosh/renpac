import platform
import shutil
import subprocess

from configparser import ConfigParser

from combos import *
from exits import *
from items import *
from rooms import *

from Config import Config
from Game import Game
from Script import Script

THIS_PATH = os.path.dirname(__file__)

class Build:
    game_name = None
    engine_path = None
    game_path = None

    @staticmethod
    def get_game_config_path() -> str:
        return f"{Build.game_path}/{Build.game_name}.cfg"
    
    @staticmethod
    def get_output_path() -> str:
        return f"{THIS_PATH}/build/{Build.game_name}/game"

    @staticmethod
    def get_game_output_file_path() -> str:
        return f"{Build.get_output_path()}/{Build.game_name}.game.rpy"

    @staticmethod
    def is_valid() -> bool:
        return Build.game_name is not None and Build.engine_path is not None and Build.game_path is not None

    @staticmethod
    def print() -> None:
        print(f"Game '{Build.game_name}'"
              f"\n\tEngine: '{Build.engine_path}'"
              f"\n\tFiles: '{Build.game_path}'"
              f"\n\tOutput: '{Build.get_output_path()}'")

def build_game() -> None:
    Config.load(Build.get_game_config_path())

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

    path = Build.get_game_output_file_path()
    print(f"writing game file to '{path}'")
    Script.write_file(path)

def build_engine() -> None:
    if platform.system() == "Windows":
        builder = "generate.bat"
    else:
        builder = "./generate.sh"

    os.chdir(Build.engine_path)

    print(f"building engine: {os.getcwd()}/{builder}")
    subprocess.run(builder)

    os.chdir(os.path.dirname(__file__))

def clean() -> None:
    shutil.rmtree(Build.get_output_path(), ignore_errors=True)

def copy_engine() -> None:
    print(f"copying engine to '{Build.get_output_path()}'")
    # TODO if building for release, include .rpyc and but exclude .rpy
    shutil.copytree(f"{Build.engine_path}/game", Build.get_output_path(), 
                    ignore=shutil.ignore_patterns("renpac-engine", "*.py", "*.pyc", "*.rpyc", "*.bak"),
                    copy_function=shutil.copy2)

def parse_build_config() -> None:
    parser = ConfigParser()
    filename = "build.cfg"
    if len(parser.read(filename)) == 0:
        raise Exception(f"could not open or no data in build config '{os.getcwd()}/{filename}'")

    print("keys:", end=' ')
    for key in parser.keys():
        print(key, end=', ')
    print("")

    Build.engine_path = parse_path(parser['engine']['path'])
    Build.game_path = parse_path(parser['game']['path'])
    Build.game_name = parser['game']['name']

def parse_path(path: str) -> str:
    # absolute
    if path.startswith('/') or ':' in path:
        return path
    # relative
    return f"{THIS_PATH}/{path}"

def main() -> None:
    parse_build_config()
    if not Build.is_valid():
        print("missing required config key for build")
        return
    Build.print()
    clean()
    build_engine()
    copy_engine()
    build_game()

if __name__ == "__main__":
    main()