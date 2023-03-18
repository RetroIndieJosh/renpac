import logging

from . import Inventory, Room, StaticClass

class Game(StaticClass):
    """! General game functionality (static class)
    """

    ## The room where the game starts
    _first_room: Room = None

    ## Whether game data is loaded
    _loaded: bool = False

    # TODO use name to load_game from appropriate file (generator will need
    # update to call it load_game_{name} instead)
    @staticmethod
    def load(name: str) -> None:
        """! Load game data 
        """
        logging.info(f"loading game")
        Inventory.clear()

        try:
            # defined by the gamebuilder
            Game._first_room = load_game() #type: ignore
        except NameError:
            raise Exception("load_game() or a symbol within not found (did you run the gamebuilder?)")
        else:
            Game._loaded = True

    @staticmethod
    def start() -> None:
        """! If the game is loaded, start it by going to the first room
        """
        if not Game._loaded:
            raise Exception("cannot start game, not loaded")
        logging.info(f"start game in '{Game._first_room.name}'")
        Room.current_set(Game._first_room)