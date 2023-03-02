import logging

from . import Hotspot, Action, Combination

def action_take(item: Hotspot):
    if type(item) is not Item:
        renpy.say("You can't take that.") #type: ignore
    else:
        item.take()

Action.register("take", action_take)

class Item(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.img_path = f"{self.name}_%s.png"

        self.action_left = Action.get("take")
        self.action_right = Action.get("use")
        self.action_middle = None

        # mouse wheel scrolling actions
        self.action_down = None
        self.action_up = None

        # a mapping of item names to funcs to trigger when used on a hotspot
        self._combinations = {}

    def add_combination(self, target: Hotspot, combo: Combination) -> None:
        if target.name in self._combinations:
            logging.warn(f"redefining combination for 'use {self.name} on {target.name}'")

        # if this is the first combination, register the "use on" action for
        # this item to replace the "use" action
        if self._combinations:
            self.action_right = Action.register(f"use {self.name} on", self.use_on)
        self._combinations[target.name] = combo

    def take(self) -> None:
        self.room.hotspot_remove(self)
        self.room = None
        global inventory_add
        inventory_add(self)

    def use_on(self, other: Hotspot) -> None:
        combo = self._combinations[other.name] if other.name in self.combinations else None
        if combo is None:
            logging.info(f"cannot combine {self.name} on {other.name}")
            renpy.say(None, f"You can't use {self.name} on {other.name}!") # type: ignore
            return

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
