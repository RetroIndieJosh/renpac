import logging
from . import StaticClass

## Turn on to show magenta boxes where hotspots are located
DEBUG_SHOW_HOTSPOTS = True

## Turn on to enable all notifications
DEBUG_NOTIFY_ALL = True

## Turn on to notify in-game when warnings occur
DEBUG_NOTIFY_WARNINGS = DEBUG_NOTIFY_ALL or False

## Turn on to notify in-game when errors occur
DEBUG_NOTIFY_ERRORS = DEBUG_NOTIFY_ALL or False

class Renpac(StaticClass):
    """! Static methods for global RenPaC features. Includs redirects for Ren'Py
    methods to avoid needing to use "#type: ignore" in the code, which could
    dangerously hide some errors/warnings."""
    @staticmethod
    def init() -> None:
        """! Initialize RenPaC. This is mostly legacy, as it used to do a lot more. TODO remove
        """
        logging.info(f"initialize RenPaC")
        renpy.show_screen("ClickArea") #type: ignore

    # Logging

    @staticmethod
    def error(message: str) -> None:
        """! Helper method to log errors that also notifies in-game if desired
        """
        logging.error(message)
        if DEBUG_NOTIFY_ERRORS:
            Renpac.notify(f"ERROR: {message}")

    @staticmethod
    def warn(message: str) -> None:
        """! Helper method to log warnings that also notifies in-game if desired
        """
        logging.warning(message)
        if DEBUG_NOTIFY_WARNINGS:
            Renpac.notify(f"WARNING: {message}")

    # Ren'Py redirect methods

    @staticmethod
    def notify(message) -> None:
        """! renpy.notify
        """
        renpy.notify(message) #type: ignore

    @staticmethod
    def narrate(what, interact: bool = True) -> None:
        """! renpy.say(who=None)
        """
        renpy.say(None, what, interact = interact) #type: ignore

    @staticmethod
    def say(who, what, interact: bool = True) -> None:
        """! renpy.say
        """
        renpy.say(who, what, interact = interact) #type: ignore

    @staticmethod
    def scene(layer="master") -> None:
        """! renpy.scene
        """
        renpy.scene(layer) #type: ignore

    @staticmethod
    def show(name, at_list=[], layer='master', what=None, zorder=0, tag=None, behind=[]) -> None:
        """! renpy.show
        """
        renpy.show(name, at_list, layer, what, zorder, tag, behind) #type: ignore