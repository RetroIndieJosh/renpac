# the main entry point for a renpac game
label renpac_start(game_name):
    show screen Debug

    show screen InventoryShower
    show screen Equipped
    show screen Fullscreen
    show screen Hotspots

    python:
        Renpac.init()
        Game.load(game_name)
        Inventory.set_mode(INVENTORY_TOP, 0.6, 0.2)

    while True:
        pause
    return