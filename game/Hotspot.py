from . import Action, Rect, Renpac

import logging

def hotspots_clear():
    renpy.hide_screen("Hotspots") # type: ignore

class Hotspot:
    _hovered = None

    @staticmethod
    def hover_clear() -> None:
        if Hotspot._hovered is None:
            return
        Hotspot._hovered.is_hovered = False
        Hotspot._hovered = None

    @staticmethod
    def hover_get() -> 'Hotspot':
        return Hotspot._hovered
    
    @staticmethod
    def hover_set(hs: 'Hotspot') -> None:
        if Hotspot._hovered is not None:
            Renpac.warn(f"overwriting existing hover target {Hotspot._hovered.name} to {hs.name}")
            Hotspot.hover_clear()
        hs.is_hovered = True
        Hotspot._hovered = hs

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

        self.rect = Rect(0, 0, 256, 256)
        self.is_hovered = False

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