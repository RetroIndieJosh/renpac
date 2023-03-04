from . import Action, Combination

import logging

def hotspots_clear():
    renpy.hide_screen("Hotspots") # type: ignore

class Hotspot:
    def __init__(self, name: str) -> None:
        self.name = name
        self.desc = None

        # default = left click, alternate = right click, middle = middle click
        self.action_left = Action.get("examine")
        self.action_right = None
        self.action_middle = None

        # mouse wheel scrolling actions
        self.action_down = None
        self.action_up = None

        self.x = 0
        self.y = 0
        self.width = 256
        self.height = 256

        self.room = None

    def delete(self):
        logging.info(f"delete hotspot {self.name}")

        global inventory
        if self in inventory:
            inventory.remove(self)
        elif self.room is not None:
            self.room.hotspot_remove(self)
        else:
            raise Exception(f"Tried to delete hotspot '{self.name}' but it doesn't exist in inventory or room!")

    def get_img_path(self) -> str:
        return None
        
    def get_lrtb(self) -> tuple:
        """! Return a tuple with values for (left, right, top, bottom).
        """
        return (self.x, self.x + self.width, self.y, self.y + self.height)