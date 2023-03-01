import logging
from . import Action, Log, Game

# TODO make this a Renpac class with static methods
# add say, show, and nofity as wrappers for equivalent renpy classes so we "type: ignore" only needs to be in this file

def renpac_init():
    config.keymap['game_menu'].remove('mouseup_3') #type: ignore
    config.keymap['hide_windows'].clear() #type: ignore

    Action.current = Action.get("take")
    if Action.current is None:
        raise Exception("Missing default action 'take'! Cannot proceed with initialization")

    Log.init()
    logging.info(f"initialized RenPaC")

def renpac_load(game_name):
    if(game_name is None):
        raise Exception("RenPaC error: no game specified.")

    Game.load("bardolf")

    logging.info(f"game '{game_name}' loaded")