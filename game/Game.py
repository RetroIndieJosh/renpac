import logging

from . import Item, Combination, Room, Exit, StaticClass

class Game(StaticClass):
    current_room: Room = None

    @staticmethod
    def load(name) -> None:
        Game.load_bardolf()

    @staticmethod
    def set_room(room):
        logging.info(f'Set room to {room.name}')

        # can't move from a room to itself
        if Game.current_room is room or room is None:
            return

        if Game.current_room is not None:
            Game.current_room.exit()

        Game.current_room = room
        renpy.scene() #type: ignore
        renpy.show(f"bg {Game.current_room.name}") #type: ignore
        Game.current_room.enter()

        renpy.notify(f"You are now in {room.name}") #type: ignore

        if(not room.visited and room.first_desc is not None):
            renpy.say(None, room.first_desc) #type: ignore
            room.visited = True

        renpy.say(None, room.desc) #type: ignore

    @staticmethod
    def update():
        Game.current_room.hotspots_show()

    # TODO replace with loading from file
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
            func = lambda: renpy.say(None, "You dump the gruel on the shackles. Great, now the mess is even worse!"),
            delete_self = True
        )
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

        gruel_stairs = Combination(
            func = lambda: renpy.say(None, "You dump the gruel down the stairs. And now you're gonna stay hungry."),
            delete_self = True
        )
        stairs_down.add_combination(gruel, gruel_stairs)

        stairs_up = Exit("stairs up")
        stairs_up.target = dungeon_cell
        stairs_up.width = 345
        stairs_up.height = 166
        guardhouse.add_hotspot(stairs_up, 1575, 0)

        # set start room
        Game.set_room(dungeon_cell) #type: ignore