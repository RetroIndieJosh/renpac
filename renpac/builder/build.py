# TODO rename to Builder.py
import logging
import shutil

from datetime import datetime
from pathlib import Path

from renpac.base import files

from renpac.base.Config import Config, ConfigEntry, ConfigType
from renpac.base.Log import Log

from renpac.builder.combos import *
from renpac.builder.exits import *
from renpac.builder.items import *
from renpac.builder.rooms import *

from renpac.builder.Game import Game
from renpac.builder.Script import Script

from renpac.builder.renpygen import RenpyGen

THIS_PATH = os.path.dirname(__file__)

log = logging.getLogger("builder")

class Builder:
    def __init__(self, root: Path, config_relative_path="build.cfg") -> None:
        self._config_path: Path = Path(root, config_relative_path)

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
        log.critical(f"Building {self._game_name} at {start_time}")

        self.print()
        self.clean()

        RenpyGen("renpac", "renpac/engine/rpy", ["base", "engine"]).generate()
        self.copy_engine_files()

        self.generate_debug_file()
        self.build_game()
        self.copy_resources()

        end_time = datetime.now()
        diff_time = (end_time - start_time).total_seconds()
        log.critical(f"Output: {self._output_path}")
        log.critical(f"Build done at {datetime.now()} ({diff_time} seconds elapsed)")

    # TODO move to Game - but causes circular deps!
    def build_game(self) -> None:
        game = Game(self._output_file_path, self._game_config_path)

        game.parse_defaults()

        # gather a lits of elements in the script so it doesn't need to be in order
        game.collect_definitions()
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
        log.info(f"** cleaning '{self._output_path}'")
        shutil.rmtree(self._output_path, ignore_errors=True)

    def copy_engine_files(self) -> None:
        log.info(f"** copying engine")
        files.copy_tree(self._engine_path, self._output_path)

    def copy_resources(self) -> None:
        mapping = {
            self._audio_path: "audio",
            self._images_path: "images",
            self._gui_path: "gui",
        }

        images = ([f"{item}_idle" for item in Game.instance().items()] 
            + [f"{item}_hover" for item in Game.instance().items()] 
            + [f"bg {room}" for room in Game.instance().rooms()])
        required_images = {resource: False for resource in images}

        def check_resource(path) -> bool:
            if "gui" in path:
                return True
            name = Path(path).stem
            extension = Path(path).suffix
            if extension == ".png" or extension == ".jpg" or extension == ".jpeg":
                if name in required_images:
                    required_images[name] = True
                    return True
                log.warning(f"unused image file")
            log.debug(f"skipped resource (cannot be validated)\n\t'{path}'")
            return False

        for source_path in mapping:
            resource_type = mapping[source_path]
            dest_path = Path(self._output_path, resource_type).resolve()
            log.info(f"copying resources ({resource_type}) from '{source_path}' to '{dest_path}'")
            files.copy_tree(source_path, dest_path, check_resource)

        for image in required_images:
            if not required_images[image]:
                log.warning(f"missing required image file '{image}'")

    def parse_config(self) -> None:
        config = Config(self._config_path)
        root_values = config.parse_section('build', {
            'root': ConfigEntry(ConfigType.STRING, True),
            'level': ConfigEntry(ConfigType.STRING, False, "debug")
        })

        root_path: Path = Path(root_values['root'])
        if not root_path.is_absolute():
            raise Exception(f"Root path must be absolute ({root_path})")
        root_path.resolve(True)

        log_level  = Log.level(root_values['level'])
        path = Path(__file__).parent.joinpath("builder.log")
        Log.init("Builder Log", path, log_level, True)
        Log.clear()

        engine_values = config.parse_section('engine', {'path': ConfigEntry(ConfigType.STRING, True)})
        self._engine_path = Path(root_path, engine_values['path']).resolve(True)
        # TODO additional validation - read Renpac.py and check known contents (validation string?)
        if not Path(self._engine_path, "Renpac.py").exists:
            raise Exception(f"Invalid engine path: no 'Renpac.py' in '{self._engine_path}'")

        game_values = config.parse_section('game', {
            'audio': ConfigEntry(ConfigType.STRING, True, "audio"),
            'author': ConfigEntry(ConfigType.STRING, False, "Anonymous"),
            'gui': ConfigEntry(ConfigType.STRING, True, "gui"),
            'images': ConfigEntry(ConfigType.STRING, True, "images"),
            'name': ConfigEntry(ConfigType.STRING, False, "Untitled RenPaC Game"),
            'path': ConfigEntry(ConfigType.STRING, True),
        })
        self._game_name = game_values['name']
        self._game_path = Path(root_path, game_values['path']).resolve(True)
        self._audio_path = Path(self._game_path, game_values['audio']).resolve(True)
        self._gui_path = Path(self._game_path, game_values['gui']).resolve(True)
        self._images_path = Path(self._game_path, game_values['images']).resolve(True)
        self.generate_paths()

        debug_values = config.parse_section('debug', {
            'hotspots': ConfigEntry(ConfigType.BOOL, True, False),
            'notify': ConfigEntry(ConfigType.STRING, True, "none"),
        })

        self._debug_lines = [
            f"DEBUG_SHOW_HOTSPOTS = {debug_values['hotspots']}"
        ]
        notify: str = debug_values['notify']
        if notify not in ['none', 'debug', 'info', 'warnings', 'errors', 'all']:
            log.warning(f"unknown value for debug.notify: '{notify}'")
        self._debug_lines.append(f"DEBUG_NOTIFY_ALL = {'True' if notify == 'all' else 'False'}")
        self._debug_lines.append("DEBUG_NOTIFY_WARNINGS = DEBUG_NOTIFY_ALL or " \
            f"{'True' if notify == 'warnings' else 'False'}")
        self._debug_lines.append("DEBUG_NOTIFY_ERRORS = DEBUG_NOTIFY_ALL or " \
            f"{'True' if notify == 'errors' else 'False'}")

    def generate_debug_file(self) -> None:
        if self._debug_lines is None:
            return
        log.info("** generating debug file")
        debug_script = Script(Path(f"{self._output_path}/debug.gen.rpy", check_exists=False), 999, self._config_path)
        debug_script.add_line(*self._debug_lines)
        debug_script.write()

    def generate_paths(self) -> None:
        self._game_config_path = Path(self._game_path, f"{self._game_name}.renpac").resolve(True)
        self._output_path = Path("build", self._game_name, "game").resolve()
        self._output_file_path = Path(self._output_path, f"{self._game_name}.game.rpy").resolve()

    def print(self) -> None:
        for line in f"PATHS" \
            f"\n\tEngine: '{self._engine_path}'" \
            f"\n\tFiles: '{self._game_path}'" \
            f"\n\tGame Config: '{self._game_config_path}'" \
            f"\n\tGame Images: '{self._images_path}'" \
            f"\n\tGame Audio: '{self._audio_path}'" \
            f"\n\tOutput: '{self._output_path}'" \
            f"\n\tOutput File: '{self._output_file_path}'".splitlines():
            log.info(line)

if __name__ == "__main__":
    build = Builder(Path(__file__).parent)
    build.build()