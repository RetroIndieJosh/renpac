init python:
    current_room = None
    active_item = None

    def clear_hotspots():
        renpy.hide_screen("Hotspots")

    def set_room(room):
        if current_room is not None:
            current_room.on_exit()

        global current_room
        current_room = room
        if current_room is None:
            return

        renpy.scene()
        renpy.show(f"bg {room.name}")
        show_hotspots()

        current_room.on_enter()
        renpy.notify(f"You are now in {room.name}")
        if(not room.visited and room.first_time_desc is not None):
            renpy.say(None, room.first_time_desc) 
        renpy.say(None, room.desc)
        room.visited = True

    def show_hotspots():
        clear_hotspots()
        renpy.show_screen("Hotspots", current_room.hotspots)

    def init_game():
        # define rooms and items in them
        dungeon_cell = Room()
        dungeon_cell.name = "cell"
        dungeon_cell.printed_name = "Tower Cell"
        dungeon_cell.desc = "A foul stench assaults you from all around. In one wall a slit serves as a window, letting in just enough light to see. Someone was kind enough to leave you a bowl of gruel."
        dungeon_cell.first_time_desc = "You wake with a vicious pounding in your head and find yourself on the upper floor of a tower. Looks like a cell."
        dungeon_cell.add_hotspot(Item("gruel"), 0.6, 0.6)
        dungeon_cell.add_hotspot(Item("shackles"), 0.8, 0.8)

        guardhouse = Room()
        guardhouse.name = "guardhouse"
        guardhouse.printed_name = "Guardhouse"
        guardhouse.desc = "This guardhouse has seen better days. Was it attacked recently? Stairs lead back up to the cell."
        dungeon_cell.add_hotspot(Exit("stairs down", guardhouse, 467, 307), 0, 782)
        guardhouse.add_hotspot(Exit("stairs up", dungeon_cell, 345, 166), 1575, 0)
    
        # set start room
        set_room(dungeon_cell)
    
    config.keymap['game_menu'].remove('K_ESCAPE')
    config.keymap['game_menu'].remove('mouseup_3')
