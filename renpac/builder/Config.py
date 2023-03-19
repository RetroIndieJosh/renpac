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

    def __init__(self, config_path: str) -> None:
        self._parser = ConfigParser()
        if len(self._parser.read(config_path)) == 0:
            raise Exception(f"could not read or no data in '{config_path}'")
        self._name = Path(config_path).name

    def get_section(self, section_key: str) -> list:
        if self._parser is None:
            printv("ERROR: config not loaded, cannot get section")
            return None
        if section_key not in self._parser:
            printv(f"ERROR: no section '{section_key}' in config")
            return None
        return self._parser[section_key]

    def key_message(self, key, section_name) -> str:
        return f"key '{key}' in section '{section_name}' of '{self._name}'"

    def sections(self) -> list:
        return self._parser.sections()

    def parse_section(self, section_name: str, entries: List[ConfigEntry]) -> Dict[str, str]:
        section = self.get_section(section_name)
        values: Dict[str, str] = {}
        for key in section:
            if key in entries:
                values[key] = section[key]
                # TODO type validation
            else:
                print(f"WARNING unknown {self.key_message(key, section_name)}")
        for key in entries:
            if key not in values:
                if entries[key].is_required:
                    raise Exception(f"ERROR missing required {self.key_message(key, section_name)}")
                else:
                    print(f"WARNING missing optional {self.key_message(key, section_name)}")
        return values