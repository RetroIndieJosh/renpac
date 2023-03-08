import logging

from Combination import *

from . import Cursor, Hotspot, Action, Combination, Renpac

class Item(Hotspot):
    _selection: 'Item' = None

    @staticmethod
    def selection_clear() -> None:
        logging.info("clear selected item")
        Item._selection = None
        Cursor.reset()

    @staticmethod
    def selection_get() -> 'Item':
        return Item._selection

    @staticmethod
    def selection_set(item: 'Item') -> None:
        logging.info(f"set selected item to '{item.name if item else 'None'}'")
        Item._selection = item
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
        combo = self._combinations[other.name] if other.name in self._combinations else None
        if combo is None:
            logging.info(f"cannot use {self.name} on {other.name}")
            renpy.say(None, f"You can't use {self.name} on {other.name}.") # type: ignore
            return

        if combo.delete_flags & TARGET_SELF or combo.replace_flags & TARGET_SELF:
            logging.debug(f"remove self ({self.name})")
            self.delete()
        if combo.delete_flags & TARGET_OTHER or combo.replace_flags & TARGET_OTHER:
            logging.debug(f"remove other ({other.name})")
            other.delete()

        if combo.replace_with is not None:
            self.room.hotspot_add(combo.replace_with)
            replace_pos = 0, 0
            if combo.replace_flags & TARGET_SELF:
                replace_pos = self.rect.get_pos()
            elif combo.replace_flags & TARGET_OTHER:
                replace_pos = other.rect.get_pos()
            combo.replace_with.rect.set_pos(*replace_pos)

        if combo.message is not None:
            Renpac.say(combo.message)
