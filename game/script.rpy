# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")

init python:
    import random

    item_count = 0
    inventory = []

    def clear_items():
        global item_count
        item_count = 0
        for i in range(0, 10):
            renpy.hide_screen(f"ShowItem{i}")

    def show_item(item):
        # TODO reset item count when room changed
        global item_count

        if(item_count >= 10):
            raise Exception("Item count exceeded maximum of 10 for room")

        renpy.show_screen(f"ShowItem{item_count}", item)

        item.in_room_id = item_count
        item_count += 1

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

        def remove_item(self, item):
            self.items.remove(item)

        def show_items(self):
            clear_items()
            for item in self.items:
                show_item(item)
    
    dungeon_cell = Room("Dungeon Cell",
        "This dilapidated cell assaults you with a foul stench. A slit in the wall serves as a window, letting in a tiny beam of light.")
    dungeon_cell.add_item(Item("gruel"))
    dungeon_cell.add_item(Item("shackles"))

    current_room = dungeon_cell

label start:
    scene bg cell

    while True:
        $ current_room.show_items()
        "[current_room.desc]"

    return

label take_item(item):
    "You take [item.name]."
    $ item.take()
    return
