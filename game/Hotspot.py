from . import Action, Rect, Renpac

import logging

## clear all hotspots in the game
def hotspots_clear():
    renpy.hide_screen("Hotspots") # type: ignore

class Hotspot:
    """! An area the player can interact with through hover and click
    """

    ## Which hotspot is currently being hovered over. Ren'py doesn't have
    ## interaction layers, so this should be one item at a time.
    _hovered = None

    @staticmethod
    def hover_clear() -> None:
        """! Clear the currently stored hovered hotspot
        """
        if Hotspot._hovered is None:
            return
        Hotspot._hovered.is_hovered = False
        Hotspot._hovered = None

    @staticmethod
    def hover_get() -> 'Hotspot':
        """! Get the hotspot where the mouse is currently hovering

        @return The Hotspot over which the mouse is hovering, or None if there
                is no such Hotspot
        """
        return Hotspot._hovered
    
    @staticmethod
    def hover_set(hs: 'Hotspot') -> None:
        """! Set the hotspot where the mouse is currently hovering. If there is
            already a hotspot in the one and only slot for storing a hovered
            hotspot, raise a warning and clear the hotspot before setting the new
            one
        """
        if hs is None:
            Hotspot.hover_clear()
            return
        if Hotspot._hovered is not None:
            Renpac.warn(f"overwriting existing hover target {Hotspot._hovered.name} to {hs.name}")
            Hotspot.hover_clear()
        hs.is_hovered = True
        Hotspot._hovered = hs

    def __init__(self, name: str) -> None:
        """! Create a hotspot
        
        @param name The unique name (handle) for the hotspot
        """

        ## The unqiue name (handle) for the hotspot
        self.name = name

        ## A description to show when the hotspot is examined
        self.desc = None

        ## An action to trigger when the hotspot is left clicked
        self.action_left = Action.get("examine")

        # TODO clean up right/middle click if we aren't going to use them

        ## An action to trigger when the hotspot is right clicked
        self.action_right = None

        ## An action to trigger when the hotspot is middle clicked
        self.action_middle = None

        ## An action to trigger when the user scrolls down on the mousewheel
        ## over the hotspot
        self.action_down = None

        ## An action to trigger when the user scrolls up on the mousewheel
        ## over the hotspot
        self.action_up = None

        ## The position and size of the hotspot for mouse detection in pixels
        self.rect = Rect(0, 0, 256, 256)

        ## Whether the hotspot is being hovered
        self.is_hovered = False

        ## The room where the hotspot exists
        self.room = None

        # TODO _deleted functionality should be in a more generalized base class
        ## Whether the hotspot has been deleted
        self._deleted = False

    # TODO _deleted functionality should be in a more generalized base class
    def delete(self):
        """! Delete the hotspot from the current game session. When the
        containing room or inventory next updates, the hotspot will be removed
        from that location.
        """
        logging.info(f"delete hotspot {self.name}")
        self._deleted = True

    def get_img_path(self) -> str:
        """! Get a path to the image to represent the hotspot. This is meant to
        be overridden by Hotspot-inheriting types that use images, such as Item.
        """
        return None

    # TODO _deleted functionality should be in a more generalized base class
    def is_deleted(self) -> bool:
        """! Get whether the Hotspot has been deleted
        """
        return self._deleted