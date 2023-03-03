import logging

from . import Renpac, Item, Combination, Room, Exit, StaticClass

class Game(StaticClass):
    current_room: Room = None

    @staticmethod
    def load(name) -> None:
        Game.load_bardolf()

    @staticmethod
    def set_room(room):
        logging.info(f"Set room to '{room.name}'")

        # can't move from a room to itself
        if Game.current_room is room or room is None:
            return

        if Game.current_room is not None:
            Game.current_room.exit()

        Game.current_room = room
        Renpac.scene()
        Renpac.show(f"bg {Game.current_room.name}")
        Game.current_room.enter()

        Renpac.notify(f"You are now in {room.name}")

        if(not room.visited and room.first_desc is not None):
            Renpac.say(None, room.first_desc)
            room.visited = True

        Renpac.say(None, room.desc)

    @staticmethod
    def update():
        Game.current_room.hotspots_show()

    @staticmethod
    def load_bardolf():
        # define rooms and items in them
        dungeon_cell = Room("cell")
        dungeon_cell.printed_name = "Tower Cell"
        dungeon_cell.desc = "A foul stench assaults you from all around. In one wall a slit serves as a window, letting in just enough light to see. Someone was kind enough to leave you a bowl of gruel."
        dungeon_cell.first_desc = "You wake with a vicious pounding in your head and find yourself on the upper floor of a tower. Looks like a cell."

        gruel = Item("gruel")
        shackles = Item("shackles")

        gruel_shackles = Combination(
            func = gruel_shackles_func,
            delete_self = True
        )
        gruel.add_combination(shackles, gruel_shackles)

        dungeon_cell.hotspot_add(gruel, 0.6, 0.6)
        dungeon_cell.hotspot_add(shackles, 0.8, 0.8)

        guardhouse = Room("guardhouse")
        guardhouse.printed_name = "Guardhouse"
        guardhouse.desc = "This guardhouse has seen better days. Was it attacked recently? Stairs lead back up to the cell."

        stairs_down = Exit("stairs down")
        stairs_down.target = guardhouse
        stairs_down.width = 467
        stairs_down.height = 307
        dungeon_cell.hotspot_add(stairs_down, 0, 782)

        gruel_stairs = Combination(
            func = gruel_stairs_func,
            delete_self = True
        )
        gruel.add_combination(stairs_down, gruel_stairs)

        stairs_up = Exit("stairs up")
        stairs_up.target = dungeon_cell
        stairs_up.width = 345
        stairs_up.height = 166
        guardhouse.hotspot_add(stairs_up, 1575, 0)

        # set start room
        Game.set_room(dungeon_cell) #type: ignore

def gruel_shackles_func():
    Renpac.say(None, "You dump the gruel on the shackles. Great, now the mess is even worse!"),

def gruel_stairs_func():
    Renpac.say(None, "You dump the gruel down the stairs. And now you're gonna stay hungry."),