class Room:
    def __init__(self, name: str) -> None:
        self.name = name
        self.printed_name = name
        self.desc = "An unknown place."

        self.visited = False
        self.first_desc = None

        self.hotspots = []

    # TODO refactor => hotspot_add
    def add_hotspot(self, hs: object, x: int, y: int) -> None:
        if(hs in self.hotspots):
            raise Exception("Tried to add hs to room but it's already there! ({hs.name} in {room.name})")

        # TODO warn if hotspot overlaps any existing hotspot

        self.hotspots.append(hs)
        hs.room = self
        hs.x = x
        hs.y = y

    # TODO refactor => hotspot_remove
    def remove_hotspot(self, hs: object) -> None:
        if(hs not in self.hotspots):
            raise Exception("Tried to remove hs to room but it's not there! ({hs.name} in {room.name})")

        self.hotspots.remove(hs)
    
    # TODO refactor => hotspots_show
    def hotspots_show(self) -> None:
        hotspots_clear() # type: ignore
        renpy.show_screen("Hotspots", self.hotspots) # type: ignore

    def enter(self) -> None:
        self.hotspots_show()
        self.on_enter()

    def exit(self) -> None:
        self.on_exit()

    # override for events to occur when entering the room
    def on_enter(self) -> None:
        pass

    # override for events to occur when exiting the room
    def on_exit(self) -> None:
        pass