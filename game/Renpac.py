import logging
from . import StaticClass

class Renpac(StaticClass):
    @staticmethod
    def init():
        config.keymap['game_menu'].remove('mouseup_3') #type: ignore
        config.keymap['hide_windows'].clear() #type: ignore

        # for easier debugging of pickle errors, should probably be removed on final build
        config.use_cpickle = False #type: ignore

        logging.info(f"initialized RenPaC")

    ###########################
    # Ren'Py redirect methods
    ###########################

    @staticmethod
    def notify(message) -> None:
        renpy.notify(message) #type: ignore

    @staticmethod
    def say(who, what, *args, **kwargs) -> None:
        renpy.say(who, what, args, kwargs) #type: ignore

    @staticmethod
    def scene(layer="master") -> None:
        renpy.scene(layer) #type: ignore

    @staticmethod
    def show(name, at_list=[], layer='master', what=None, zorder=0, tag=None, behind=[]) -> None:
        renpy.show(name, at_list, layer, what, zorder, tag, behind) #type: ignore