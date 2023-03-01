import logging

from . import Hotspot, Action 

class Item(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.img_path = f"{self.name}_%s.png"
        self.action = Action.register(f"use {name} on", self.use_on)

    def use_on(self, other: Hotspot) -> None:
        combo = self.combinations[other.name] if other.name in self.combinations else None
        if combo is None:
            logging.info(f"cannot combine {self.name} on {other.name}")
            renpy.say(None, f"You can't use {self.name} on {other.name}!") # type: ignore
            return

        # TODO active_item should be in a Game or RenPaC class
        global active_item
        if combo.delete_self:
            logging.debug(f"remove self ({self.name})")
            if active_item is self:
                active_item = None
            self.delete()
        if combo.delete_other:
            logging.debug(f"remove other ({other.name})")
            if active_item is other:
                active_item = None
            other.delete()

        if combo.func is not None:
            combo.func()
