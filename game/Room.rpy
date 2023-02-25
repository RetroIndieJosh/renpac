init python:
    class Room:
        def __init__(self, name, desc):
            self.name = name
            self.desc = desc
            self.items = []

        def add_item(self, item):
            if(item in self.items):
                raise Exception("Tried to add item to room but it's already there! ({item.name} in {room.name})")

            self.items.append(item)
            item.room = self
            # TODO if this is the current room, clear all items then call show_items

        def make_current(self):
            global current_room
            current_room = self
        
            renpy.scene()
            renpy.show(f"bg {self.name}")
            self.show_items()
    
        def remove_item(self, item):
            self.items.remove(item)
    
        def show_items(self):
            clear_items()
            for item in self.items:
                show_item(item)
