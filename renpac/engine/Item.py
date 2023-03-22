import logging

from typing import Dict, Optional

from renpac.base.target import *

from renpac.engine.Action import Action
from renpac.engine.Combination import Combination
from renpac.engine.Cursor import Cursor
from renpac.engine.Hotspot import Hotspot
from renpac.engine.Renpac import Renpac

class Item(Hotspot):
    """! An item that the player can collect and use represented by an image and interacted through a Hotspot
    """

    ## The currently selected item for "use on" action
    _selection: Optional['Item'] = None

    @staticmethod
    def selection_clear() -> None:
        """! Clear the currently selected item
        """
        logging.info("clear selected item")
        Item._selection = None
        Cursor.reset()

    @staticmethod
    def selection_get() -> Optional['Item']:
        """! Get the currently selected item

        @return The currently selected Item, or None if no selection
        """
        return Item._selection

    @staticmethod
    def selection_set(item: 'Item') -> None:
        """! Set the currently selected item

        @param item The Item to select
        """
        logging.info(f"set selected item to '{item.name if item else 'None'}'")
        Item._selection = item
        Cursor.set(item.name)

    def __init__(self, name: str) -> None:
        """! Create an item

        @param name The unique name (handle) for the item
        """
        super().__init__(name)

        ## Path to the idle image for when the item is drawn
        self.img_path_idle = f"{self.name}_idle.png"

        ## Path to the hover image for when the mouse is hovering over the item
        self.img_path_hover = f"{self.name}_hover.png"

        ## Whether the item is fixed in place (cannot be taken)
        self.fixed = False

        # set inherited Hotspot actions
        self.action_left = Action.get("take")
        self.action_right = Action.get("use")
        self.action_middle = Action.get("examine")
        self.action_down = None
        self.action_up = None

        ## A mapping of item names to Combinations to trigger when used on a
        ## hotspot that matches the key name
        self._combinations: Dict[str, Combination] = {}

        ## A custom message for taking the item. If this is left as None, the
        ## default message "You take {name}" will be used.
        self.take_message = None

    def add_combination(self, other: Hotspot, combo: Combination) -> None:
        """! Add a combination for reacting to "use on" action
        
        @param target The hotspot that this item will be "used on" for the
                      combination to trigger
        @param combo The Combination defining what happens when the "use on"
                     action occurs
        """
        if other.name in self._combinations:
            logging.warn(f"redefining combination for 'use {self.name} on {other.name}'")
        self._combinations[other.name] = combo

    def delete(self) -> None:
        """! Delete the item from the current game session. In addition to
        removing the hotspot, also removes it as the selected item if it is.
        """
        if Item.selection_get() is self:
            Item.selection_clear()
        super().delete()

    def get_img_path(self) -> Optional[str]:
        """! Get the path to the relevant image for the item, based on hover state
        
        @return The path to the image for the item
        """
        if self.is_hovered:
            return self.img_path_hover
        return self.img_path_idle

    # TODO make sure this isn't duplicating functionality of the cleanup when
    # rooms cycle through to clear deleted items
    def remove_from_room(self) -> None:
        """! Remove the hotspot from its containing room.
        """
        if self.room is None:
            return
        self.room.hotspot_remove(self)
        self.room = None

    def use_on(self, other: Hotspot) -> None:
        """! Use this item on another one (trigger Combination)
        
        @param other The target item for using, i.e. "use self on other"
        """
        logging.debug(f"combos in {self.name}: {self._combinations}")
        combo: Optional[Combination] = self._combinations[other.name] if other.name in self._combinations else None
        if combo is None:
            logging.info(f"cannot use {self.name} on {other.name}")
            Renpac.narrate(f"You can't use {self.name} on {other.name}.")
            return

        if combo.delete_flags & TARGET_SELF or combo.replace_flags & TARGET_SELF:
            logging.debug(f"remove self ({self.name})")
            self.delete()
        if combo.delete_flags & TARGET_OTHER or combo.replace_flags & TARGET_OTHER:
            logging.debug(f"remove other ({other.name})")
            other.delete()

        if combo.replace_with is not None:
            replace_pos = 0, 0
            if combo.replace_flags & TARGET_SELF:
                self.room.hotspot_add(combo.replace_with)
                replace_pos = self.rect.get_pos()
            elif combo.replace_flags & TARGET_OTHER:
                other.room.hotspot_add(combo.replace_with)
                replace_pos = other.rect.get_pos()
            combo.replace_with.rect.set_pos(*replace_pos)

        if combo.message is not None:
            Renpac.narrate(combo.message)
