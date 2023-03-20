from configparser import ConfigParser, SectionProxy
from enum import Enum
from pathlib import Path
from typing import Any, Dict

class ConfigType(Enum):
    STRING = 0
    LITERAL = 1 # for numbers, functions, and references to other objects
    BOOL = 2
    POSITION = 3
    SIZE = 4
    INT = 5
    FLOAT = 6
    LIST = 7

class ConfigEntry:
    expected_type: ConfigType
    is_required: bool
    fallback = None

    def __init__(self, expected_type: ConfigType, is_required: bool, fallback = None) -> None:
        self.expected_type = expected_type
        self.is_required = is_required
        self.fallback = fallback

# TODO if this isn't specific to the game config, reuse for build config and
# make non-static; Game can contain the game config, Build can contain the build
# config
class Config:
    _name: str
    _parser: ConfigParser

    def __init__(self, config_path: str) -> None:
        self._parser = ConfigParser()
        if len(self._parser.read(config_path)) == 0:
            raise Exception(f"could not read or no data in '{config_path}'")
        self._name = Path(config_path).name

    def get_section(self, section_key: str) -> SectionProxy:
        if section_key not in self._parser:
            raise Exception(f"ERROR: no section '{section_key}' in config")
        return self._parser[section_key]

    def key_message(self, key, section_name) -> str:
        return f"key '{key}' in section '{section_name}' of '{self._name}'"

    def sections(self) -> list:
        return self._parser.sections()

    def parse_section(self, section_name: str, entries: Dict[str, ConfigEntry]) -> Dict[str, Any]:
        section = self.get_section(section_name)
        values: Dict[str, Any] = {}
        for key in [key for key in section if key in entries]:
            if entries[key].expected_type == ConfigType.BOOL:
                values[key] = self._parser.getboolean(section_name, key)
            elif entries[key].expected_type == ConfigType.FLOAT:
                values[key] = self._parser.getfloat(section_name, key)
            elif entries[key].expected_type == ConfigType.INT:
                values[key] = self._parser.getint(section_name, key)
            else:
                values[key] = section[key]

        for key in [key for key in section if key not in entries]:
            print(f"WARNING unknown {self.key_message(key, section_name)}")

        for key in [key for key in entries if key not in values]:
            if entries[key].fallback is None:
                if entries[key].is_required:
                    raise Exception(f"ERROR missing required {self.key_message(key, section_name)}")
                print(f"WARNING missing optional with no fallback {self.key_message(key, section_name)}")
            else:
                values[key] = entries[key].fallback
        return values