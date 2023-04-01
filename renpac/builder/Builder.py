# TODO rename to Builder.py
import logging
import shutil

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from renpac.base import files

from renpac.base.Config import Config, ConfigEntry, Type
from renpac.base.Log import Log

from renpac.builder import issues
from renpac.builder import renpac

from renpac.builder.GameScript import GameScript
from renpac.builder.renpygen import RenpyGen
from renpac.builder.RenpyScript import RenpyScript

log = logging.getLogger("builder")

ALLOWED_IMAGE_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg"]

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

        start_time: datetime = datetime.now()
        build_message: str = f"Building {self._game_name} at {start_time}"
        print(build_message)
        log.info(build_message)

        self.print()
        self.clean()

        game: renpac.Game = renpac.Game(self._game_source_path)
        script: Optional[GameScript] = self.build_game_script(game)
        if script is not None:
            if self.check_resources(game):
                RenpyGen("renpac", "renpac/engine/rpy", ["base", "engine"]).generate()
                self.copy_engine_files()
                self.generate_debug_file()
                script.write()
                self.copy_resources()

        end_time = datetime.now()
        diff_time = (end_time - start_time).total_seconds()
        end_message: str = f"Output: {self._output_path}\n" \
            f"Build done at {datetime.now()} ({diff_time} seconds elapsed)"
        print(end_message)
        log.info(end_message)

        issues.Manager.print()

    def build_game_script(self, game: renpac.Game) -> Optional[GameScript]:
        game.dump_to_log()
        script = game.generate_script(self._game_source_path, self._game_output_path) 
        return script

    def clean(self) -> None:
        log.info(f"** cleaning '{self._output_path}'")
        shutil.rmtree(self._output_path, ignore_errors=True)

    def copy_engine_files(self) -> None:
        log.info(f"** copying engine")
        files.copy_tree(self._engine_path.joinpath('rpy'), self._output_path)

    def resource_dir_paths(self) -> List[Path]:
        return [
            self._audio_path,
            self._images_path,
            self._gui_path,
        ]

    def check_resources(self, game: renpac.Game) -> bool:
        items: List[str] = game.get_items()
        rooms: List[str] = game.get_rooms()

        images = ([f"{item}_idle" for item in items] 
            + [f"{item}_hover" for item in items]
            + [f"bg {room}" for room in rooms])
        required_image_found = {resource: False for resource in images}

        resource_path: Path
        image_files: List[Path] = list(self._images_path.iterdir())
        for resource_path in files.filter_files(image_files, ALLOWED_IMAGE_EXTENSIONS):
            name: str = resource_path.stem
            if name in required_image_found:
                required_image_found[name] = True
                continue
            issues.Manager.add_warning(f"[RES] unused image file {resource_path}")

        for image in required_image_found:
            if not required_image_found[image]:
                issues.Manager.add_error(f"[RES] missing required image file '{image}' in '{self._images_path}'")

        return issues.Manager.has_error() or issues.Manager.has_warning()

    def copy_resources(self):
        for source_path in self.resource_dir_paths():
            resource_type = source_path.name
            dest_path = Path(self._output_path, resource_type).resolve()
            log.info(f"copying resources ({resource_type}) from '{source_path}' to '{dest_path}'")
            files.copy_tree(source_path, dest_path, lambda path: path.suffix in [".png", ".jpg", ".jpeg"])

    def parse_config(self) -> None:
        config = Config(self._config_path)
        root_values = config.parse_section('build', {
            'root': ConfigEntry(Type.STRING, True),
            'level': ConfigEntry(Type.STRING, False, "debug")
        })

        root_path: Path = Path(root_values['root'])
        if not root_path.is_absolute():
            raise Exception(f"Root path must be absolute ({root_path})")
        root_path.resolve(True)

        log_level  = Log.level(root_values['level'])
        path = Path(__file__).parent.joinpath("builder.log")
        Log.init("Builder Log", path, log_level, True)
        Log.clear()

        engine_values = config.parse_section('engine', {'path': ConfigEntry(Type.STRING, True)})
        self._engine_path = Path(root_path, engine_values['path']).resolve(True)
        # TODO additional validation - read Renpac.py and check known contents (validation string?)
        if not Path(self._engine_path, "Renpac.py").exists():
            raise Exception(f"Invalid engine path: no 'Renpac.py' in '{self._engine_path}'")

        game_values = config.parse_section('game', {
            'audio': ConfigEntry(Type.STRING, True, "audio"),
            'author': ConfigEntry(Type.STRING, False, "Anonymous"),
            'gui': ConfigEntry(Type.STRING, True, "gui"),
            'images': ConfigEntry(Type.STRING, True, "images"),
            'name': ConfigEntry(Type.STRING, False, "Untitled RenPaC Game"),
            'path': ConfigEntry(Type.STRING, True),
        })
        self._game_name = game_values['name']
        self._game_path = Path(root_path, game_values['path']).resolve(True)
        self._audio_path = Path(self._game_path, game_values['audio']).resolve(True)
        self._gui_path = Path(self._game_path, game_values['gui']).resolve(True)
        self._images_path = Path(self._game_path, game_values['images']).resolve(True)
        self.generate_paths()

        debug_values = config.parse_section('debug', {
            'hotspots': ConfigEntry(Type.BOOL, True, False),
            'notify': ConfigEntry(Type.STRING, True, "none"),
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
        debug_script = RenpyScript(Path(f"{self._output_path}/debug.gen.rpy", check_exists=False), 999, str(self._config_path))
        debug_script.add_python(*self._debug_lines)
        debug_script.write()

    def generate_paths(self) -> None:
        self._game_source_path = Path(self._game_path, f"{self._game_name}.renpac").resolve(True)
        self._output_path = Path("build", self._game_name, "game").resolve()
        self._game_output_path = Path(self._output_path, f"{self._game_name}.game.rpy").resolve()

    def print(self) -> None:
        for line in f"PATHS" \
            f"\n\tEngine: '{self._engine_path}'" \
            f"\n\tFiles: '{self._game_path}'" \
            f"\n\tGame Config: '{self._game_source_path}'" \
            f"\n\tGame Images: '{self._images_path}'" \
            f"\n\tGame Audio: '{self._audio_path}'" \
            f"\n\tOutput: '{self._output_path}'" \
            f"\n\tOutput File: '{self._game_output_path}'".splitlines():
            log.info(line)

if __name__ == "__main__":
    build = Builder(Path(__file__).parent)
    build.build()