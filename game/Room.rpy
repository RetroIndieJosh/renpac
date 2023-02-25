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

            # refresh hotspots if we added to the current room
            global current_room
            if current_room == self:
                self.show_hotspots()

        def enter(self):
            global current_room
            current_room = self
        
            renpy.scene()
            renpy.show(f"bg {self.name}")
            self.show_hotspots()
    
        def remove_hotspot(self, hs):
            self.hotspots.remove(hs)
    
        def show_hotspots(self):
            clear_hotspots()
            for hs in self.hotspots:
                show_hotspot(hs)