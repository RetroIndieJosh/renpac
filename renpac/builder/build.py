# TODO rename to Build.py
import shutil
import pathlib
import platform

from configparser import ConfigParser
from datetime import datetime

from renpac.base.printv import *

from renpac.base import files

from renpac.builder.combos import *
from renpac.builder.exits import *
from renpac.builder.items import *
from renpac.builder.rooms import *

from renpac.builder.Config import Config
from renpac.builder.Game import Game
from renpac.builder.Path import Path
from renpac.builder.Script import Script

from renpac.builder.generate import generate

THIS_PATH = os.path.dirname(__file__)

class Build:
    def __init__(self, config_path="build.cfg") -> None:
        self._config_path = Path(config_path)
        self._debug_lines = None
        self._game_name = None
        self._game_path = None
        self._engine_path = None
        self._audio_path = None
        self._images_path = None
        self._gui_path = None

    def build(self) -> None:
        self.parse_config()
        start_time = datetime.now()
        print(f"Building {self._game_name} at {start_time}")
        self.print()
        self.clean()
        self.generate_engine_rpy()
        self.copy_engine_files()
        self.generate_debug_file()
        self.build_game()
        self.copy_resources()
        end_time = datetime.now()
        diff_time = (end_time - start_time).total_seconds()
        print(f"Output: {self._output_path}")
        print(f"Build done at {datetime.now()} ({diff_time} seconds elapsed)")

    def generate_engine_rpy(self) -> None:
        generate(f"../engine", f"../engine/rpy")

    # TODO move to Game - but causes circular deps!
    def build_game(self) -> None:
        config_path = f"{self._game_path}/{self._game_name}.cfg"
        game = Game(self._output_file_path, config_path)

        game.parse_defaults()

        # gather a lits of elements in the script so it doesn't need to be in order
        game.parse_definitions()
        game.report_definitions()

        # must be in order items, rooms, exits, combos
        game.all_items(parse_item)
        game.all_rooms(parse_room)
        game.all_exits(parse_exit)
        game.all_combos(parse_combo)

        game.parse_game()
        game.parse_inventory()

        game.finalize()

        game.write()

    def clean(self) -> None:
        path = self._output_path.get()
        printv(f"cleaning '{path}'")
        shutil.rmtree(path, ignore_errors=True)

    def copy_engine_files(self) -> None:
        source_path = Path(f"../engine/rpy").get()
        dest_path = self._output_path.get()
        printv(f"copying engine from '{source_path}' to '{dest_path}'")
        files.copy_tree(source_path, dest_path)

    def copy_resources(self) -> None:
        mapping = {
            self._audio_path: "audio",
            self._images_path: "images",
            self._gui_path: "gui",
        }

        images = [f"{item}_idle" for item in Game.instance().items()] 
        images += [f"{item}_hover" for item in Game.instance().items()] 
        images += [f"bg {room}" for room in Game.instance().rooms()]
        required_images = {resource: False for resource in images}

        def check_resource(path) -> bool:
            if "gui" in path:
                return True
            name = pathlib.Path(path).stem
            extension = pathlib.Path(path).suffix
            if extension == ".png" or extension == ".jpg" or extension == ".jpeg":
                if name in required_images:
                    required_images[name] = True
                    return True
                else:
                    print(f"WARNING unused image file")
            print(f"WARNING skipped resource (cannot be validated)\n\t'{path}'")
            return False

        for source_path in mapping:
            resource_type = mapping[source_path]
            dest_path = Path(f"{self._output_path}/{resource_type}", False)
            printv(f"copying resources ({resource_type}) from '{source_path}' to '{dest_path}'")
            files.copy_tree(source_path.get(), dest_path.get(), check_resource)

        for image in required_images:
            if not required_images[image]:
                print(f"WARNING missing required image file '{image}'")

    def parse_config(self) -> None:
        parser = ConfigParser()
        if len(parser.read(self._config_path.get())) == 0:
            raise Exception(f"could not open or no data in build config '{self._config_path}'")

        if 'root' not in parser['build']:
            raise Exception("Root path must be set in 'build' section of build.cfg")
        # TODO validate root path is a valid path
        root_path = parser['build']['root']
        if root_path.startswith('/'):
            if platform.system() == "Windows":
                raise Exception(f"Illegal root path for Windows.\n\tRoot: {root_path}")
        elif platform.system() != "Windows":
                raise Exception(f"Illegal root path for Linux.\n\tRoot: {root_path}")

        if parser.getboolean('build', 'verbose', fallback=False):
            enable_verbose()

        required_path_sections = ['engine', 'game']
        for section in required_path_sections:
            if section not in parser:
                raise Exception(f"ERROR: No '{section}' section in build config {self._config_path}")
            if 'path' not in parser[section]:
                raise Exception(f"ERROR: No 'path' defined in '{section}' section in build config {self._config_path}")

        # TODO rewrite to use variable mapping thingy (will first need some adjustments)
        self._engine_path = Path('/'.join([root_path, parser['engine']['path']]))
        self._game_path = Path('/'.join([root_path, parser['game']['path']]))

        # TODO optional, so would flag as such in variable map (and also set default)
        if 'audio' in parser['game']:
            audio_path_relative = parser['game']['audio']
        else:
            audio_path_relative = "audio"
        self._audio_path = Path(f"{self._game_path}/{audio_path_relative}")

        # TODO ditto above
        if 'images' in parser['game']:
            images_path_relative = parser['game']['images']
        else:
            images_path_relative = "images"
        self._images_path = Path(f"{self._game_path}/{images_path_relative}")

        # TODO ditto above
        if 'gui' in parser['game']:
            gui_path_relative = parser['game']['gui']
        else:
            gui_path_relative = "audio"
        self._gui_path = Path(f"{self._game_path}/{gui_path_relative}")

        if 'name' not in parser['game']:
            raise Exception(f"ERROR: No 'name' defined in 'game' section in build config {self._config_path}")

        if 'debug' in parser:
            self._debug_lines = [
                f"DEBUG_SHOW_HOTSPOTS = {parser.getboolean('debug', 'hotspots', fallback=False)}"
            ]
            notify = "none"
            if 'notify' in parser['debug']:
                notify = parser['debug']['notify']
            if notify not in ['none', 'warnings', 'errors', 'all']:
                print(f"WARNING unknown value for debug.notify: '{notify}'")
            self._debug_lines.append(f"DEBUG_NOTIFY_ALL = {'True' if notify == 'all' else 'False'}")
            self._debug_lines.append(f"DEBUG_NOTIFY_WARNINGS = DEBUG_NOTIFY_ALL or {'True' if notify == 'warnings' else 'False'}")
            self._debug_lines.append(f"DEBUG_NOTIFY_ERRORS = DEBUG_NOTIFY_ALL or {'True' if notify == 'errors' else 'False'}")

        self._game_name = parser['game']['name']
        self.generate_paths()

    def generate_debug_file(self) -> None:
        if self._debug_lines is None:
            return
        printv("generating debug file")
        debug_script = Script(f"{self._output_path}/debug.gen.rpy", 999, self._config_path)
        debug_script.add_lines(self._debug_lines)
        debug_script.write()

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