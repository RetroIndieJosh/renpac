from . import Hotspot, Renpac

class Room:
    def __init__(self, name: str) -> None:
        self.name = name
        self.printed_name = name
        self.desc = "An unknown place."

        self.visited = False
        self.first_desc = None

        self.hotspots = []

    def hotspot_add(self, hs: Hotspot, x: int, y: int) -> None:
        if(hs in self.hotspots):
            raise Exception("Tried to add hs to room but it's already there! ({hs.name} in {room.name})")

        self.hotspots.append(hs)
        hs.room = self
        hs.x = x
        hs.y = y

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