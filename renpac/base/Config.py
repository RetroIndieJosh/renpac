import logging

from configparser import ConfigParser, SectionProxy
from enum import Enum
from pathlib import Path
from typing import Any, Dict

log = logging.getLogger("Config")

# TODO move to a more centralized location
class Type(Enum):
    STRING = 0
    # for anything printed literally, like a reference to another object
    # should NOT be used for other types as it bypasses checks
    # TODO add ROOM, ITEM, EXIT, COMBO types for checking vs game definitions
    LITERAL = 1 
    BOOL = 2
    # TODO distinguish between COORD_INT and COORD_FLOAT and COORD_DOUBLE
    # TODO also SIZE_INT, SIZE_FLOAT, SIZE_DOUBLE which must be non-negative
    # (for now we only deal with positive integer coordinates)
    COORD = 3
    INT = 4
    FLOAT = 5
    LIST = 6

# TODO move these with type enum
TRUE_BOOLS = ["true", "yes", "1"]
def is_true(value: str) -> bool:
    return value.lower() in TRUE_BOOLS
FALSE_BOOLS = ["false", "no", "0"]
def is_false(value: str) -> bool:
    return value.lower() in FALSE_BOOLS

class ConfigEntry:
    expected_type: Type
    is_required: bool
    fallback = None

    def __init__(self, expected_type: Type, is_required: bool, 
            fallback = None) -> None:
        self.expected_type = expected_type
        self.is_required = is_required
        self.fallback = fallback

# TODO if this isn't specific to the game config, reuse for build config and
# make non-static; Game can contain the game config, Build can contain the build
# config
class Config:
    _name: str
    _parser: ConfigParser

    def __init__(self, config_path: Path) -> None:
        self._parser = ConfigParser()
        if len(self._parser.read(config_path)) == 0:
            raise Exception(f"could not read or no data in '{config_path}'")
        self._name = config_path.name

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
            if entries[key].expected_type == Type.BOOL:
                values[key] = self._parser.getboolean(section_name, key)
            elif entries[key].expected_type == Type.FLOAT:
                values[key] = self._parser.getfloat(section_name, key)
            elif entries[key].expected_type == Type.INT:
                values[key] = self._parser.getint(section_name, key)
            else:
                values[key] = section[key]

        for key in [key for key in section if key not in entries]:
            log.warning(f"unknown {self.key_message(key, section_name)}")

        for key in [key for key in entries if key not in values]:
            if entries[key].fallback is None:
                if entries[key].is_required:
                    raise Exception(f"missing required {self.key_message(key, section_name)}")
                log.warning(f"missing optional with no fallback {self.key_message(key, section_name)}")
            else:
                values[key] = entries[key].fallback
        return values