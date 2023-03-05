import logging
from . import StaticClass

class Renpac(StaticClass):
    @staticmethod
    def init() -> None:
        logging.info(f"initialize RenPaC")
        renpy.show_screen("ClickArea") #type: ignore

    # Mouse

    @staticmethod
    def mouse_reset() -> None:
        global default_mouse
        default_mouse = "default"

    @staticmethod
    def mouse_set(mouse_name: str) -> None:
        global config
        if mouse_name not in config.mouse:
            Renpac.warn(f"no mouse cursor '{mouse_name}' in config")

        global default_mouse
        default_mouse = mouse_name

    # Logging

    @staticmethod
    def error(message: str) -> None:
        logging.error(message)
        Renpac.notify(f"ERROR: {message}")

    @staticmethod
    def warn(message: str) -> None:
        logging.warning(message)
        Renpac.notify(f"WARNING: {message}")

    # Ren'Py redirect methods

    @staticmethod
    def notify(message) -> None:
        renpy.notify(message) #type: ignore

    @staticmethod
    def narrate(what, interact: bool = True) -> None:
        renpy.say(None, what, interact = interact) #type: ignore

    @staticmethod
    def say(who, what, interact: bool = True) -> None:
        renpy.say(who, what, interact = interact) #type: ignore

    @staticmethod
    def scene(layer="master") -> None:
        renpy.scene(layer) #type: ignore

    @staticmethod
    def show(name, at_list=[], layer='master', what=None, zorder=0, tag=None, behind=[]) -> None:
        renpy.show(name, at_list, layer, what, zorder, tag, behind) #type: ignore