init python:
    import random

    class Hotspot:
        def __init__(self, name):
            self.name = name
            self.img_path = None
    
            # TODO come up with a less silly way to set these
            global item_count
            self.x = item_count * 0.2
            self.y = 0.4
    
            self.room = None
            self.in_room_id = -1

            self.on_click = None
    
    # TODO move to Item.rpy
    class Item(Hotspot):
        def __init__(self, name):
            super(name)
            self.img_path = f"{self.name}_%s.png"
            # TODO update Item things to call Hotspot::on_click instead of Item::take
            self.on_click = self.take

        def take(self):
            self.room.remove_item(self)
            self.room = None
   
            self.in_room_id = -1
    
            global inventory
            inventory.append(self)
  