import logging

from . import Inventory, Room, StaticClass

class Game(StaticClass):
    _first_room: Room = None
    _loaded: bool = False

    @staticmethod
    def load(name: str) -> None:
        logging.info(f"load game '{name}'")
        Inventory.clear()

        # defined by the gamebuilder
        try:
            Game._first_room = load_game() #type: ignore
        except NameError:
            raise Exception("load_game() or a symbol within not found (did you run the gamebuilder?)")
        else:
            Game._loaded = True

    @staticmethod
    def start() -> None:
        if not Game._loaded:
            raise Exception("cannot start game, not loaded")
        logging.info(f"start game in '{Game._first_room.name}'")
        Room.current_set(Game._first_room)