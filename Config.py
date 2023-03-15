from printv import printv

from configparser import ConfigParser

# TODO rename to GameConfig
class Config:
    _parser: ConfigParser = None

    filename: str = None

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
    def load(config_filename: str) -> None:
        Config._parser = ConfigParser()
        Config.filename = config_filename
        if len(Config._parser.read(Config.filename)) == 0:
            raise Exception(f"could not open or no data in game config '{Config.filename}'")

    @staticmethod
    def sections() -> list:
        if Config._parser is None:
            printv("ERROR: config not loaded, cannot get sections")
            return None
        return Config._parser.sections()
