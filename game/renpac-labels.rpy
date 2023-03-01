# the main entry point for a renpac game
label renpac(game_name, debug=False):
    python:
        Renpac.init()
        Renpac.load(game_name)
        # TODO this should be set by game config
        set_inventory_mode(INVENTORY_TOP, 0.6, 0.2)

    if debug:
        show screen Debug

    show screen InventoryShower
    show screen Equipped
    show screen Fullscreen

    while True:
        $ Game.update()
        pause
    
    return