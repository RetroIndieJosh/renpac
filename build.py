import filecmp
import platform
import shutil
import subprocess

from configparser import ConfigParser
from Path import Path

from printv import *

from combos import *
from exits import *
from items import *
from rooms import *

from Config import Config
from Game import Game
from Script import Script

import argparse
parser = argparse.ArgumentParser()
 
parser.add_argument("-f", "--force", action='store_true', help = "Force Overwrite: Copy all files, even if they match the destination.")
parser.add_argument("-v", "--verbose", action='store_true', help = "Verbose Mode: Show additional process messages")
 
args = vars(parser.parse_args())
FORCE_OVERWRITE = args['force']
if args['verbose']:
    enable_verbose()

THIS_PATH = os.path.dirname(__file__)

class Build:
    def __init__(self, config_path="build.cfg") -> None:
        self._config_path = Path(config_path)
        self._game_name = None
        self._game_path = None
        self._engine_path = None
        self._images_path = None
        self._audio_path = None

    def build(self) -> None:
        self.parse_config()
        print(f"Building {self._game_name}")
        self.print()
        self.clean()
        self.build_engine()
        self.copy_engine()
        self.build_game()
        self.copy_resources()
        print(f"Build done")

    def build_engine(self) -> None:
        builder = "generate.bat" if platform.system() == "Windows" else "./generate.sh"
        engine_path = self._engine_path.get()

        printv(f"building engine: {engine_path}/{builder}")
        os.chdir(engine_path)
        subprocess.run(builder)
        os.chdir(THIS_PATH)

    # TODO move to Game - but causes circular deps!
    def build_game(self) -> None:
        Config.load(f"{self._game_path}/{self._game_name}.cfg")

        # gather a lits of elements in the script so it doesn't need to be in order
        Game.parse_definitions()
        Game.report_definitions()

        # must be in order items, rooms, exits, combos
        Game.all_items(parse_item)
        Game.all_rooms(parse_room)
        Game.all_exits(parse_exit)
        Game.all_combos(parse_combo)

        Game.parse_game()
        Game.parse_inventory()

        Game.finalize()

        path = self._output_file_path
        printv(f"writing game file to '{path}'")
        Script.write_file(path.get())

    def clean(self) -> None:
        path = self._output_path.get()
        printv(f"cleaning '{path}'")
        shutil.rmtree(path, ignore_errors=True)

    def copy_engine(self) -> None:
        # this is weird but it gets us a clean-looking path; doesn't make sense
        # to store the /game path and we need the base engine path to get the
        # engine builder script
        source_path = Path(f"{self._engine_path}/game").get()
        dest_path = self._output_path.get()
        printv(f"copying engine from '{source_path}' to '{dest_path}'")
        self.copy_files(source_path, dest_path)
        # TODO if building for release, include .rpyc and but exclude .rpy
        #shutil.copytree(source_path, dest_path, 
                        #ignore=shutil.ignore_patterns("renpac-engine", "*.py", "*.pyc", "*.rpyc", "*.bak"),
                        #copy_function=shutil.copy2)

    def copy_files(self, source_dir: str, dest_dir: str, relative_dir: str = ""):
        dir = os.path.join(source_dir, relative_dir)
        for file in os.listdir(dir):
            source_file = os.path.join(source_dir, relative_dir, file)
            if os.path.isdir(source_file):
                self.copy_files(source_dir, dest_dir, os.path.join(relative_dir, file))
            else:
                printv(f"[{relative_dir}] ", end='')
                dest_file = os.path.join(dest_dir, relative_dir, file)
                if not FORCE_OVERWRITE:
                    # skip copy if the destination file matches exactly
                    if os.path.exists(dest_file):
                        if os.path.getsize(source_file) == os.path.getsize(dest_file):
                            if filecmp.cmp(source_file, dest_file, False):
                                printv(f"SKIP\n\t{source_file}")
                                continue
                printv(f"COPY\n\t{source_file}\n\tTO {dest_file}")
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(source_file, dest_file)

    def copy_resources(self) -> None:
        mapping = {
            self._audio_path: "audio",
            self._images_path: "images",
        }
        for source_path in mapping:
            resource_type = mapping[source_path]
            dest_path = Path(f"{self._output_path}/{resource_type}", False)
            printv(f"copying resources ({resource_type}) from '{source_path}' to '{dest_path}'")
            self.copy_files(source_path.get(), dest_path.get())
            # TODO figure out what ignores we want for this (maybe none? or customizable in build config?)
            #shutil.copytree(source_path.get(), dest_path.get(),
                            #ignore=shutil.ignore_patterns("renpac-engine", "*.py", "*.pyc", "*.rpyc", "*.bak"),
                            #copy_function=shutil.copy2)

    def parse_config(self) -> None:
        parser = ConfigParser()
        if len(parser.read(self._config_path.get())) == 0:
            raise Exception(f"could not open or no data in build config '{self._config_path}'")

        required_path_sections = ['engine', 'game']
        for section in required_path_sections:
            if section not in parser:
                raise Exception(f"ERROR: No '{section}' section in build config {self._config_path}")
            if 'path' not in parser[section]:
                raise Exception(f"ERROR: No 'path' defined in '{section}' section in build config {self._config_path}")

        # TODO rewrite to use variable mapping thingy (will first need some adjustments)
        self._engine_path = Path(parser['engine']['path'])
        self._game_path = Path(parser['game']['path'])

        # TODO optional, so would flag as such in variable map (and also set default)
        if 'audio' in parser['game']:
            audio_path_relative = parser['game']['audio']
        else:
            audio_path_relative = "audio"
        self._audio_path = Path(f"{self._game_path}/{audio_path_relative}")

        # TODO ditto above
        if 'images' in parser['game']:
            images_path_relative = Path(parser['game']['images'])
        else:
            images_path_relative = "images"
        self._images_path = Path(f"{self._game_path}/{images_path_relative}")

        if 'name' not in parser['game']:
            raise Exception(f"ERROR: No 'name' defined in 'game' section in build config {self._config_path}")

        self._game_name = parser['game']['name']
        self.generate_paths()

    def generate_paths(self) -> None:
        self._game_config_path = Path(f"{self._game_path}/{self._game_name}.cfg")
        self._output_path = Path(f"build/{self._game_name}/game", False)
        self._output_file_path = Path(f"{self._output_path}/{self._game_name}.game.rpy", False)

    def print(self) -> None:
        printv(f"Paths:"
              f"\n\tEngine: '{self._engine_path}'"
              f"\n\tFiles: '{self._game_path}'"
              f"\n\tGame Config: '{self._game_config_path}'"
              f"\n\tGame Images: '{self._images_path}'"
              f"\n\tGame Audio: '{self._audio_path}'"
              f"\n\tOutput: '{self._output_path}'"
              f"\n\tOutput File: '{self._output_file_path}'\n\n")

def main() -> None:
    build = Build()
    build.build()

if __name__ == "__main__":
    main()