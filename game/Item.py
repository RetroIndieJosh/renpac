import logging

from . import Hotspot, Action, Combination

class Item(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.img_path_idle = f"{self.name}_idle.png"
        self.img_path_hover = f"{self.name}_hover.png"

        # whether the item is fixed in place (cannot be taken)
        self.fixed = False

        self.action_left = Action.get("take")
        self.action_right = Action.get("use")
        self.action_middle = Action.get("examine")

        # mouse wheel scrolling actions
        self.action_down = None
        self.action_up = None

        # a mapping of item names to funcs to trigger when used on a hotspot
        self._combinations = {}

        self.take_message = None

    def add_combination(self, target: Hotspot, combo: Combination) -> None:
        if target.name in self._combinations:
            logging.warn(f"redefining combination for 'use {self.name} on {target.name}'")

        # if this is the first combination, register the "use on" action for
        # this item to replace the "use" action
        if self._combinations:
            self.action_right = Action.register(f"use {self.name} on", self.use_on)
        self._combinations[target.name] = combo

    def get_img_path(self) -> str:
        if self.is_hovered:
            return self.img_path_hover
        return self.img_path_idle

    def remove_from_room(self) -> None:
        self.room.hotspot_remove(self)
        self.room = None

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
