current_room = None
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

def init_game():
    dungeon_cell = Room("Dungeon Cell",
        "This dilapidated cell assaults you with a foul stench. A slit in the wall serves as a window, letting in a tiny beam of light.")
    dungeon_cell.add_item(Item("gruel"))
    dungeon_cell.add_item(Item("shackles"))

    global current_room
    current_room = dungeon_cell