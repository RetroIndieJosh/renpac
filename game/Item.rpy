init python:
    import random
  
    class Item:
        def __init__(self, name):
            self.name = name
            self.img_path = f"{self.name}_%s.png"
    
            # TODO come up with a less silly way to set these
            global item_count
            self.x = random.randrange(5) * 0.2
            self.y = 0.4
    
            self.room = None
            self.in_room_id = -1
    
        def take(self):
            self.room.remove_item(self)
            self.room = None
   
            self.in_room_id = -1
    
            global inventory
            inventory.append(self)
