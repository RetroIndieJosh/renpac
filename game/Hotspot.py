from . import Combination

import logging

def hotspots_clear():
    renpy.hide_screen("Hotspots") # type: ignore

class Hotspot:
    def __init__(self, name: str) -> None:
        # TODO name must be unique since we're using it as key, probably best to
        # have all hotspots use unique names so these can identify them
        # (would it be better to store in a game dict instead of name being part of hotspot?)
        # (or use a unique ID that increments instead? it's silly to have name
        # clashes, but what if there's something in multiplicity like coins?)

        self.name = name
        self.desc = name
        self.img_path = None

        self.x = 0
        self.y = 0
        self.width = 256
        self.height = 256

        # a mapping of item names to funcs to trigger when item is used on this hotspot
        self.combinations = dict()

        self.room = None

    def add_combination(self, item: object, combination: Combination):
        if item.name in self.combinations:
            raise Exception(f"{item.name} is already a key in combinations for {self.name}!")
        self.combinations[item.name] = combination
    
    def click(self):
        global active_item

        if active_item is None:
            logging.debug(f"no active item, do regular click on hotspot {self.name}")
            self.on_click()
            return

        logging.debug(f"active item is {active_item.name}, try {self.name}.combine({active_item.name})")
        combo = self.combine(active_item)
        if combo is None:
            logging.info(f"cannot combine {active_item.name} on {self.name}")
            renpy.say(None, f"You can't use {active_item.name} on {self.name}!") # type: ignore
            return

        # TODO maybe this should be delete_active or delete_actor? since "self" can be confusing (self is target, but self is active item O_O)
        if combo.delete_self:
            logging.debug(f"remove self ({active_item.name})")
            active_item.delete()
        if combo.delete_target:
            logging.debug(f"remove target ({self.name})")
            self.delete()

        active_item = None

        # do func last in case it includes an execution-ender such as renpy.say()
        if combo.func is not None:
            combo.func()

    def delete(self):
        logging.info(f"delete hotspot {self.name}")

        global inventory
        if self in inventory:
            inventory.remove(self)
        elif self.room is not None:
            self.room.remove_hotspot(self)
        else:
            raise Exception(f"Tried to delete hotspot '{self.name}' but it doesn't exist in inventory or room!")

    def on_click(self) -> None:
        raise NotImplementedError()

    # combine item with this hotspot
    def combine(self, item: object) -> Combination:
        return self.combinations[item.name] if item.name in self.combinations else None