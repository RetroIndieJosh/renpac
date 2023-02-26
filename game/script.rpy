# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")

define DEBUG_SHOW_HOTSPOTS = True
define DEBUG_NOTIFY_HOTSPOTS = True
define DEBUG_INVENTORY_SHOWER = True

label start:
    $ init_game()

    menu:
        "Where should the inventory be anchored?"

        "Bottom":
            $ set_inventory_mode(INV_BOTTOM)
        "Top":
            $ set_inventory_mode(INV_TOP)
        "Left":
            $ set_inventory_mode(INV_LEFT)
        "Right":
            $ set_inventory_mode(INV_RIGHT)

    #show screen Debug
    show screen InventoryShower
    show screen Unequip

    while True:
        $ show_hotspots()
        window hide
        pause

    return
