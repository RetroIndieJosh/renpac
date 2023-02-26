class Room:
    def __init__(self):
        self.name = "room"
        self.printed_name = "Room"
        self.desc = "An unknown place."

        self.visited = False
        self.first_time_desc = None

        self.hotspots = []

    def add_hotspot(self, hs, x, y):
        if(hs in self.hotspots):
            raise Exception("Tried to add hs to room but it's already there! ({hs.name} in {room.name})")

        self.hotspots.append(hs)
        hs.room = self
        hs.x = x
        hs.y = y

    def remove_hotspot(self, hs):
        self.hotspots.remove(hs)

    def enter(self):
        self.on_enter()

    def exit(self):
        pass

    # can be overridden for events to occur when entering the room
    def on_enter(self):
        pass

    # can be overridden for events to occur when exiting the room
    def on_exit(self):
        pass