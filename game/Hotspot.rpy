init python:
    import random

    class Hotspot:
        def __init__(self, name):
            self.name = name
            self.img_path = None
    
            self.x = 0
            self.y = 0
            self.width = 256
            self.height = 256
    
            self.room = None

        def on_click(self):
            raise NotImplementedError()

    class Exit(Hotspot):
        def __init__(self, name, target_room, width, height):
            super().__init__(name)
            self.target_room = target_room
            self.width = width
            self.height = height

        def on_click(self):
            self.target_room.enter()
    
    class Item(Hotspot):
        def __init__(self, name):
            super().__init__(name)
            self.img_path = f"{self.name}_%s.png"

        def on_click(self):
            self.room.remove_hotspot(self)
            self.room = None
            inventory_add(self)
  
label click(hs):
    $ hs.on_click()
    return