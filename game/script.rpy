# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")

define DEBUG_SHOW_HOTSPOTS = True
define DEBUG_NOTIFY_HOTSPOTS = True

label start:
    $ init_game()

    while True:
        show screen Debug
        $ renpy.show_screen("InventoryShower", inventory)
        #show screen InventoryShower(inventory)
        show screen Unequip
        window hide
        pause

    return
