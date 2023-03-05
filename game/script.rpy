# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")

label ask_inventory_pos:
    menu:
        "Where should the inventory be anchored?"

        "Bottom":
            $ Inventory.set_mode(INVENTORY_BOTTOM, 0.6, 0.2)
        "Top":
            $ Inventory.set_mode(INVENTORY_TOP, 0.6, 0.2)
        "Left":
            $ Inventory.set_mode(INVENTORY_LEFT, 0.6, 0.1)
        "Right":
            $ Inventory.set_mode(INVENTORY_RIGHT, 0.6, 0.1)

label start:
    call renpac_start("bardolf")
    return
