init python:
    HOTSPOT_MAX = 10

    current_room = None
    hs_count = 0

    def clear_hotspots():
        global hs_count
        hs_count = 0

        for i in range(0, HOTSPOT_MAX):
            renpy.hide_screen(f"Hotspot{i}")

    def show_hotspot(hs):
        if(hs_count >= HOTSPOT_MAX):
            raise Exception("Item count exceeded maximum of 10 for room")

        renpy.show_screen(f"Hotspot{hs_count}", hs)

        global hs_count
        hs_count += 1

    def init_game():
        # define rooms and items in them
        dungeon_cell = Room("cell",
            "This dilapidated cell assaults you with a foul stench. A slit in the wall serves as a window, letting in a tiny beam of light.")
        dungeon_cell.add_hotspot(Item("gruel"), 0.6, 0.6)
        dungeon_cell.add_hotspot(Item("shackles"), 0.8, 0.9)

        guardhouse = Room("guardhouse", "")
        dungeon_cell.add_hotspot(Exit("stairs down", guardhouse, 467, 307), 0, 782)
        guardhouse.add_hotspot(Exit("stairs up", dungeon_cell, 345, 166), 1575, 0)
    
        # set start room
        global current_room
        dungeon_cell.enter()