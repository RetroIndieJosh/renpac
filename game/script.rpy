# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")

init python:
    import random

    item_count = 0

    def clear_items():
        for i in range(0, 10):
            renpy.hide_screen(f"ShowItem{i}")

    def show_item(item):
        # TODO reset item count when room changed
        global item_count

        if(item_count > 10):
            raise Exception("Item count exceeded maximum of 10 for room")

        renpy.show_screen(f"ShowItem{item_count}", item.name, item.img_path, item.x, item.y)

        item.in_room_id = item_count
        item_count += 1

    class Item:
        def __init__(self, name):
            self.name = name
            self.img_path = f"{self.name}_%s.png"

            # TODO come up with a less silly way to set these
            global item_count
            self.x = random.randrange(5) * 0.2
            self.y = random.randrange(5) * 0.2

            self.in_room_id = -1

        def take(self):
            renpy.hide_screen(f"ShowItem[self.in_room_id]")
            self.in_room_id = -1

    class Room:
        def __init__(self, desc):
            self.desc = desc
            self.items = []

        def add_item(self, item):
            self.items.append(item)
            # TODO if this is the current room, clear all items then call show_items

        def show_items(self):
            clear_items()
            for item in self.items:
                show_item(item)
    
    dungeon_cell = Room("You wake in a dirty cell. A slit in the wall serves as a window, letting in a tiny beam of light.")
    dungeon_cell.add_item(Item("gruel"))
    dungeon_cell.add_item(Item("shackles"))

    current_room = dungeon_cell

label start:
    scene bg cell

    while True:
        $ current_room.show_items()
        "[current_room.desc]"

    return

label take_item(name):
    "You take [name]."
    return
