from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from renpac.base.printv import *

from configparser import ConfigParser

@dataclass
class ConfigEntry:
    expected_type: int
    is_required: bool

# TODO if this isn't specific to the game config, reuse for build config and
# make non-static; Game can contain the game config, Build can contain the build
# config
class Config:
    _name: str = None
    _parser: ConfigParser = None

    @staticmethod
    def get_section(section_key: str) -> list:
        if Config._parser is None:
            printv("ERROR: config not loaded, cannot get section")
            return None
        if section_key not in Config._parser:
            printv(f"ERROR: no section '{section_key}' in config")
            return None
        return Config._parser[section_key]

    @staticmethod
    def load(config_path: str) -> None:
        Config._parser = ConfigParser()
        if len(Config._parser.read(config_path)) == 0:
            raise Exception(f"could not open or no data in game config '{config_path}'")
        Config._name = Path(config_path).name

    @staticmethod
    def sections() -> list:
        if Config._parser is None:
            printv("ERROR: config not loaded, cannot get sections")
            return None
        return Config._parser.sections()

    @staticmethod
    def key_message(key, section_name) -> str:
        return f"key '{key}' in section '{section_name}' of '{Config._name}'"

    @staticmethod
    def parse_section(section_name: str, entries: List[ConfigEntry]) -> Dict[str, str]:
        section = Config.get_section(section_name)
        values: Dict[str, str] = {}
        for key in section:
            if key in entries:
                values[key] = section[key]
                # TODO type validation
            else:
                print(f"WARNING unknown {Config.key_message(key, section_name)}")
        for key in entries:
            if key not in values:
                if entries[key].is_required:
                    raise Exception(f"ERROR missing required {Config.key_message(key, section_name)}")
                else:
                    print(f"WARNING missing optional {Config.key_message(key, section_name)}")
        return values