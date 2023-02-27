# TODO make this a renpy label
label set_room(room):
    $ global current_room

    # can't move from a room to itself
    if current_room is room or room is None:
        return

    if current_room is not None:
        $ current_room.exit()

    python:
        current_room = room
        renpy.scene()
        renpy.show(f"bg {current_room.name}")
        current_room.enter()

    $ renpy.notify(f"You are now in {room.name}")

    if(not room.visited and room.first_desc is not None):
        "[room.first_desc]"
        $ room.visited = True

    "[room.desc]"
    return

label renpac(game_name, debug=False):
    python:
        renpac_init()
        renpac_load(game_name)
        set_inventory_mode(INVENTORY_TOP, 0.6, 0.2)

    if debug:
        show screen Debug

    show screen InventoryShower
    show screen Equipped
    show screen Fullscreen

    # TODO this loop should be in the game as well, maybe started with a game_run()
    while True:
        $ current_room.hotspots_show()
        pause
    
    return