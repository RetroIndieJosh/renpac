import logging

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from renpac.base.Log import Log
from renpac.base.StaticClass import StaticClass

@dataclass(frozen = True)
class Message:
    who: Optional[str]
    what: str

class Renpac(StaticClass):
    """! Static methods for global RenPaC features. Includs redirects for Ren'Py
    methods to avoid needing to use "#type: ignore" in the code, which could
    dangerously hide some errors/warnings."""

    _messages: List[Message] = []
    _log: Log

    @staticmethod
    def init() -> None:
        """! Initialize RenPaC. This is mostly legacy, as it used to do a lot more. TODO remove
        """
        Log.init(Path(__file__, "renpac.log"), logging.DEBUG)
        renpy.show_screen("ClickArea") #type: ignore

    # Logging

    @staticmethod
    def error(message: str) -> None:
        """! Helper method to log errors that also notifies in-game if desired
        """
        Log.get("renpac").error(message)
        if DEBUG_NOTIFY_ERRORS: #type:ignore
            Renpac.notify(f"ERROR: {message}")

    @staticmethod
    def warn(message: str) -> None:
        """! Helper method to log warnings that also notifies in-game if desired
        """
        Log.get("renpac").warning(message)
        if DEBUG_NOTIFY_WARNINGS: #type:ignore
            Renpac.notify(f"WARNING: {message}")

    # Ren'Py redirect methods

    @staticmethod
    def notify(message) -> None:
        """! renpy.notify
        """
        renpy.notify(message) #type: ignore

    @staticmethod
    def narrate(what) -> None:
        """! renpy.say(who=None)
        """
        Renpac.say(None, what)

    @staticmethod
    def say(who, what) -> None:
        """! renpy.say
        """
        Renpac._messages.append(Message(who, what))

    @staticmethod
    def can_hover() -> bool:
        return len(Renpac._messages) <= 1

    @staticmethod
    def next_say():
        if len(Renpac._messages) == 0:
            return ""
        next_say = Renpac._messages[0]
        if len(Renpac._messages) > 1:
            Renpac._messages = Renpac._messages[1:]
        return next_say

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

if __name__ == "__main__":
    print("no tests available")