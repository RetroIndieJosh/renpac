# the main entry point for a renpac game
label renpac_start(game_name):
    show screen Debug

    show screen InventoryScreen
    show screen Equipped
    show screen Hotspots

    python:
        Renpac.init()
        Game.load(game_name)
        Inventory.set_mode(INVENTORY_BOTTOM, 1100, 200)
        Game.start()

    while True:
        pause
    return