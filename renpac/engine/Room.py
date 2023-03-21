import logging

from typing import List, Optional

from renpac.engine.Hotspot import Hotspot
from renpac.engine.Item import Item
from renpac.engine.Renpac import Renpac

class Room:
    """! A location containing Hotspots for the player to interact with and a background image
    """

    # TODO make private
    ## The current room where the player resides
    current: Optional['Room'] = None

    @staticmethod
    def current_set(room: 'Room') -> None:
        """! Set the current room (location of the player)
        
        @param room The Room to set
        """
        logging.info(f"set room to '{room.name}'")

        # can't move from a room to itself
        if Room.current is room or room is None:
            return

        Item.selection_clear()
        Hotspot.hover_clear()

        if Room.current is not None:
            Room.current.exit()

        Room.current = room
        Room.current.enter()

    def __init__(self, name: str) -> None:
        """! Create a room

        @param name The unique name (handle) for the room
        """

        ## The unique name (handle) for the room
        self.name = name

        ## The name printed when the room is referenced in player-facing text
        self.printed_name = name

        ## A description for the room printed when the player enters
        self.desc = "An unknown place."

        # TODO make private with visit() method
        ## Whether the player has previously visited the room
        self.visited = False

        ## A description to print before the regular description when the player
        ## enters the room for the first time
        self.first_desc = None

        # TODO make private
        self.hotspots: List[Hotspot] = []

    def clear_deleted(self) -> None:
        """! Clear any hotspots in the room that have been deleted
        """
        self.hotspots = [item for item in self.hotspots if not item.is_deleted()]

    def hotspot_add(self: 'Room', hs: Hotspot) -> None:
        """! Add a hotspot to the room
        
        @param hs The hotspot to add
        """
        if(hs in self.hotspots):
            raise Exception("Tried to add hs to room but it's already there! ({hs.name} in {room.name})")
        self.hotspots.append(hs)
        hs.room = self

    def hotspot_remove(self, hs: Hotspot) -> None:
        """! Remove a hotspot from the room
        
        @param hs The hotspot to remove
        """
        if(hs not in self.hotspots):
            raise Exception("Tried to remove hs to room but it's not there! ({hs.name} in {room.name})")
        self.hotspots.remove(hs)

    def enter(self) -> None:
        """! Send the player to this room. Print necessary descriptions and set up hotspots.
        """
        Renpac.scene()
        Renpac.show(f"bg {self.name}")

        self.on_enter()

        # end with narrate because for some reason it kicks us out of the function!
        # and it also doesn't know how to handle a {p} tag! it just erases everything after it!
        if(not self.visited and self.first_desc is not None):
            self.visited = True
            Renpac.narrate(self.first_desc)
        Renpac.narrate(self.desc)

    def exit(self) -> None:
        """! Called when the player leaves the room to trigger any on exit events.
        """
        self.on_exit()

    def on_enter(self) -> None:
        """! Called when the player enters the room, before showing any
        descriptions. Set or override to react as needed.
        """
        pass

    # override for events to occur when exiting the room
    def on_exit(self) -> None:
        """! Called when the player exits the room. Set or override to react as
        needed.
        """
        pass