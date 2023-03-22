# TODO rename to Build.py
import shutil
import pathlib
import platform

from datetime import datetime

from renpac.base.printv import enable_verbose, printv

from renpac.base import files

from renpac.builder.combos import *
from renpac.builder.exits import *
from renpac.builder.items import *
from renpac.builder.rooms import *

from renpac.base.Config import Config, ConfigEntry, ConfigType

from renpac.builder.Game import Game
from renpac.builder.Path import Path
from renpac.builder.Script import Script

from renpac.builder.generate import generate

THIS_PATH = os.path.dirname(__file__)

class Build:
    def __init__(self, config_path="build.cfg") -> None:
        self._config_path: Path = Path(config_path)

        self._debug_lines: List[str]
        self._game_name: str
        self._game_path: Path
        self._engine_path: Path
        self._audio_path: Path
        self._images_path: Path
        self._gui_path: Path

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
        generate(f"..", f"../engine/rpy", ["base", "engine"])

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
        config = Config(self._config_path.get())
        root_values = config.parse_section('build', {
            'root': ConfigEntry(ConfigType.STRING, True),
            'verbose': ConfigEntry(ConfigType.BOOL, False, False),
        })

        root_path: str = root_values['root']
        if root_path.startswith('/'):
            if platform.system() == "Windows":
                raise Exception(f"Illegal root path for Windows.\n\tRoot: {root_path}")
        elif platform.system() != "Windows":
                raise Exception(f"Illegal root path for Linux.\n\tRoot: {root_path}")

        if root_values['verbose']:
            enable_verbose()

        game_values = config.parse_section('game', {
            'audio': ConfigEntry(ConfigType.STRING, True, "audio"),
            'author': ConfigEntry(ConfigType.STRING, False, "Anonymous"),
            'gui': ConfigEntry(ConfigType.STRING, True, "gui"),
            'images': ConfigEntry(ConfigType.STRING, True, "images"),
            'name': ConfigEntry(ConfigType.STRING, False, "Untitled RenPaC Game"),
            'path': ConfigEntry(ConfigType.STRING, True),
        })
        self._game_path = Path('/'.join([root_path, game_values['path']]))

        self._game_name = game_values['name']
        self.generate_paths()

        engine_values = config.parse_section('engine', {'path': ConfigEntry(ConfigType.STRING, True)})
        self._engine_path = Path('/'.join([root_path, engine_values['path']]))

        audio_path_relative = game_values['audio']
        self._audio_path = Path(f"{self._game_path}/{audio_path_relative}")

        gui_path_relative = game_values['gui']
        self._gui_path = Path(f"{self._game_path}/{gui_path_relative}")

        images_path_relative = game_values['images']
        self._images_path = Path(f"{self._game_path}/{images_path_relative}")

        debug_values = config.parse_section('debug', {
            'hotspots': ConfigEntry(ConfigType.BOOL, True, False),
            'notify': ConfigEntry(ConfigType.STRING, True, "none"),
        })

        self._debug_lines = [
            f"DEBUG_SHOW_HOTSPOTS = {debug_values['hotspots']}"
        ]
        notify: str = debug_values['notify']
        if notify not in ['none', 'debug', 'info', 'warnings', 'errors', 'all']:
            print(f"WARNING unknown value for debug.notify: '{notify}'")
        self._debug_lines.append(f"DEBUG_NOTIFY_ALL = {'True' if notify == 'all' else 'False'}")
        self._debug_lines.append("DEBUG_NOTIFY_WARNINGS = DEBUG_NOTIFY_ALL or " \
            f"{'True' if notify == 'warnings' else 'False'}")
        self._debug_lines.append("DEBUG_NOTIFY_ERRORS = DEBUG_NOTIFY_ALL or " \
            f"{'True' if notify == 'errors' else 'False'}")

    def generate_debug_file(self) -> None:
        if self._debug_lines is None:
            return
        printv("generating debug file")
        debug_script = Script(Path(f"{self._output_path}/debug.gen.rpy", check_exists=False), 999, self._config_path)
        debug_script.add_line(*self._debug_lines)
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

if __name__ == "__main__":
    build = Build()
    build.build()