from . import Action, Combination

import logging

def hotspots_clear():
    renpy.hide_screen("Hotspots") # type: ignore

class Hotspot:
    def __init__(self, name: str) -> None:
        self.name = name
        self.desc = name
        self.img_path = None

        # default = left click, alternate = right click, middle = middle click
        self.action_default = Action.get("examine")
        self.action_alternate = None
        self.action_middle = None

        # mouse wheel scrolling actions
        self.action_down = None
        self.action_up = None

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
    
    def delete(self):
        logging.info(f"delete hotspot {self.name}")

        global inventory
        if self in inventory:
            inventory.remove(self)
        elif self.room is not None:
            self.room.hotspot_remove(self)
        else:
            raise Exception(f"Tried to delete hotspot '{self.name}' but it doesn't exist in inventory or room!")