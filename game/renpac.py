import logging
from . import Room, Item, Combination, Exit, Action, Log

current_room: Room = None

# TODO replace with loading from file
def game_load_bardolf():
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
    renpy.call("set_room", dungeon_cell) # type: ignore

def renpac_init():
    config.keymap['game_menu'].remove('mouseup_3') #type: ignore
    config.keymap['hide_windows'].clear() #type: ignore

    Action.current = Action.get("take")
    if Action.current is None:
        raise Exception("Missing default action 'take'! Cannot proceed with initialization")

    Log.init()
    logging.info(f"initialized RenPaC")

def renpac_load(game_name):
    if(game_name is None):
        raise Exception("RenPaC error: no game specified.")

    game_load_bardolf()
    logging.info(f"game '{game_name}' loaded")