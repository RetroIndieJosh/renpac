import logging

from . import Hotspot, Item, Renpac

class Room:
    # TODO make private
    current = None

    @staticmethod
    def current_set(room: 'Room') -> None:
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
        self.name = name
        self.printed_name = name
        self.desc = "An unknown place."

        # TODO make private with visit() method
        self.visited = False
        self.first_desc = None

        # TODO make private
        self.hotspots = []

    def clear_deleted(self) -> None:
        self.hotspots = [item for item in self.hotspots if not item.is_deleted()]

    def hotspot_add(self, hs: Hotspot) -> None:
        if(hs in self.hotspots):
            raise Exception("Tried to add hs to room but it's already there! ({hs.name} in {room.name})")
        self.hotspots.append(hs)
        hs.room = self

    def hotspot_remove(self, hs: Hotspot) -> None:
        if(hs not in self.hotspots):
            raise Exception("Tried to remove hs to room but it's not there! ({hs.name} in {room.name})")
        self.hotspots.remove(hs)

    def enter(self) -> None:
        Renpac.scene()
        Renpac.show(f"bg {self.name}")

        self.on_enter()

        # end with narrate because for some reason it kicks us out of the function!
        # and it also doesn't know how to handle a {p} tag! it just erases everything after it!
        if(not self.visited and self.first_desc is not None):
            self.visited = True
            Renpac.narrate(f"{self.first_desc} {self.desc}")
        else:
            Renpac.narrate(self.desc)

    def exit(self) -> None:
        self.on_exit()

    # override for events to occur when entering the room
    def on_enter(self) -> None:
        pass

    # override for events to occur when exiting the room
    def on_exit(self) -> None:
        pass