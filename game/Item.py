import logging

from . import Cursor, Hotspot, Action, Combination, Renpac

class Item(Hotspot):
    _selected: 'Item' = None

    @staticmethod
    def selection_clear() -> None:
        logging.info("clear selected item")
        Item._selected = None
        Cursor.reset()

    @staticmethod
    def selection_get() -> 'Item':
        return Item._selected

    @staticmethod
    def selection_set(item: 'Item') -> None:
        logging.info(f"set selected item to '{item.name if item else 'None'}'")
        Item._selected = item
        Cursor.set(item.name)

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
        # TODO register this as a general "use on" action, two targets? or automtaically reference active item
        #if self._combinations:
            #self.action_right = Action(f"use {self.name} on", self.use_on)
        self._combinations[target.name] = combo

    def delete(self) -> None:
        if Item.selection_get() is self:
            Item.selection_clear()
        super().delete()

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
            renpy.say(None, f"You can't use {self.name} on {other.name}.") # type: ignore
            return

        if combo.delete_self:
            logging.debug(f"remove self ({self.name})")
            self.delete()
        if combo.delete_other:
            logging.debug(f"remove other ({other.name})")
            other.delete()

        if combo.func is not None:
            combo.func()
