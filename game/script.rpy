# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")

define DEBUG_SHOW_HOTSPOTS = True
define DEBUG_NOTIFY_HOTSPOTS = True
define DEBUG_INVENTORY_SHOWER = True

# TODO set this with a config file (or renpac file)
label ask_inventory_pos:
    menu:
        "Where should the inventory be anchored?"

        "Bottom":
            $ set_inventory_mode(INVENTORY_BOTTOM, 0.6, 0.2)
        "Top":
            $ set_inventory_mode(INVENTORY_TOP, 0.6, 0.2)
        "Left":
            $ set_inventory_mode(INVENTORY_LEFT, 0.6, 0.1)
        "Right":
            $ set_inventory_mode(INVENTORY_RIGHT, 0.6, 0.1)

label start:
    python:
        game_init("bardolf")
        set_inventory_mode(INVENTORY_TOP, 0.6, 0.2)

    #show screen Debug
    # TODO move these to game_init (this is the client-side script and shouldn't have any RenPaC stuff)
    show screen InventoryShower
    show screen Equipped
    show screen Fullscreen

    # TODO this loop should be in the game as well, maybe started with a game_run()
    while True:
        $ current_room.hotspots_show()
        pause

    return
