init python:
    class Room:
        def __init__(self, name, desc):
            self.name = name
            self.desc = desc
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

        def on_enter(self):
            if DEBUG_ROOM_CHANGE:
                renpy.notify(f"entered {self.name}")

        def on_exit(self):
            if DEBUG_ROOM_CHANGE:
                renpy.notify(f"exited {self.name}")