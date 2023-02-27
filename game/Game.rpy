init python:
    current_room = None

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
        if(not room.visited and room.first_desc is not None):
            renpy.say(None, room.first_desc) 
        renpy.say(None, room.desc)
        room.visited = True

    def show_hotspots():
        clear_hotspots()
        renpy.show_screen("Hotspots", current_room.hotspots)

    def init_game():
        # define rooms and items in them
        dungeon_cell = Room("cell")
        dungeon_cell.printed_name = "Tower Cell"
        dungeon_cell.desc = "A foul stench assaults you from all around. In one wall a slit serves as a window, letting in just enough light to see. Someone was kind enough to leave you a bowl of gruel."
        dungeon_cell.first_desc = "You wake with a vicious pounding in your head and find yourself on the upper floor of a tower. Looks like a cell."

        gruel = Item("gruel")
        shackles = Item("shackles")

        gruel_shackles = Combination()
        gruel_shackles.delete_self = True
        gruel_shackles.func = lambda: renpy.say(None, "You dump the gruel on the shackles. Great, now the mess is even worse!")
        shackles.add_combination(gruel, gruel_shackles)

        dungeon_cell.add_hotspot(gruel, 0.6, 0.6)
        dungeon_cell.add_hotspot(shackles, 0.8, 0.8)

        guardhouse = Room("guardhouse")
        guardhouse.printed_name = "Guardhouse"
        guardhouse.desc = "This guardhouse has seen better days. Was it attacked recently? Stairs lead back up to the cell."

        stairs_down = Exit("stairs down")
        stairs_down.target = guardhouse
        stairs_down.width = 467
        stairs_down.height = 307
        dungeon_cell.add_hotspot(stairs_down, 0, 782)

        gruel_stairs = Combination()
        gruel_stairs.delete_self = True
        gruel_stairs.func = lambda: renpy.say(None, "You dump the gruel down the stairs. And now you're gonna stay hungry.")
        stairs_down.add_combination(gruel, gruel_stairs)

        stairs_up = Exit("stairs up")
        stairs_up.target = dungeon_cell
        stairs_up.width = 345
        stairs_up.height = 166
        guardhouse.add_hotspot(stairs_up, 1575, 0)
    
        # set start room
        set_room(dungeon_cell)
    
    #config.keymap['game_menu'].remove('K_ESCAPE')
    config.keymap['game_menu'].remove('mouseup_3')
    config.keymap['hide_windows'].clear()