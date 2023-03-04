import logging
from . import StaticClass

class Renpac(StaticClass):
    @staticmethod
    def init():
        logging.info(f"initialized RenPaC")

    ###########################
    # Ren'Py redirect methods
    ###########################

    @staticmethod
    def notify(message) -> None:
        renpy.notify(message) #type: ignore

    @staticmethod
    def narrate(message, interact: bool = True) -> None:
        Renpac.say(None, message, interact)

    @staticmethod
    def say(who, what, interact: bool = True) -> None:
        renpy.say(who, what, interact = interact) #type: ignore

    @staticmethod
    def scene(layer="master") -> None:
        renpy.scene(layer) #type: ignore

    @staticmethod
    def show(name, at_list=[], layer='master', what=None, zorder=0, tag=None, behind=[]) -> None:
        renpy.show(name, at_list, layer, what, zorder, tag, behind) #type: ignore