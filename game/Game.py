import logging

from . import Combination, Exit, Hotspot, Inventory, Item, Renpac, Room, StaticClass

class Game(StaticClass):
    _first_room: Room = None

    @staticmethod
    def load(name: str) -> None:
        logging.info(f"load game '{name}'")
        Inventory.clear()
        Game.load_bardolf()

    @staticmethod
    def start() -> None:
        logging.info(f"start game in '{Game._first_room.name}'")
        Room.current_set(Game._first_room)

    @staticmethod
    def load_bardolf():
        dungeon_cell = Room("cell")
        dungeon_cell.printed_name = "Tower Cell"
        dungeon_cell.desc = ("A foul stench assaults you from all around. In one "
            "wall a slit serves as a window, letting in just enough light to see.")
        dungeon_cell.first_desc = ("You wake with a vicious pounding in your head "
            "and find yourself on the upper floor of a tower. Looks like a cell.")

        gruel = Item("gruel")
        gruel.take_message = ("You almost vomit as you approach the stinky "
            "gruel, but take it in case you're hungry enough to eat it later.")
        dungeon_cell.hotspot_add(gruel, 1150, 630)
        gruel.rect.set_size(100, 75)

        shackles = Item("shackles")
        shackles.desc = "Rusty shackles chain you to the ground. They don't look too strong, though."
        shackles.fixed = True

        gruel_shackles = Combination(
            func = gruel_shackles_func,
            delete_self = True
        )
        gruel.add_combination(shackles, gruel_shackles)

        dungeon_cell.hotspot_add(shackles, 800, 900)

        guardhouse = Room("guardhouse")
        guardhouse.printed_name = "Guardhouse"
        guardhouse.desc = "This guardhouse has seen better days. Was it attacked recently? Stairs lead back up to the cell."

        stairs_down = Exit("stairs down")
        stairs_down.target = guardhouse
        stairs_down.rect.set_size(467, 306)
        dungeon_cell.hotspot_add(stairs_down, 0, 782)

        gruel_stairs = Combination(
            func = gruel_stairs_func,
            delete_self = True
        )
        gruel.add_combination(stairs_down, gruel_stairs)

        stairs_up = Exit("stairs up")
        stairs_up.target = dungeon_cell
        stairs_up.rect.set_size(345, 166)
        guardhouse.hotspot_add(stairs_up, 1575, 0)

        Game._first_room = dungeon_cell

def gruel_shackles_func():
    Renpac.narrate("You dump the gruel on the shackles. Great, now the mess is even worse!"),

def gruel_stairs_func():
    Renpac.narrate("You dump the gruel down the stairs. And now you're gonna stay hungry."),