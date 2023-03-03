import logging

from . import Action, Area, Hotspot, Item, Renpac, StaticClass

def action_take(item: Hotspot):
    if type(item) is not Item:
        Renpac.say("You can't take that.")
    else:
        Inventory.add(item)
    #renpy.block_rollback() #type: ignore

Action.register("take", action_take)

class Inventory(StaticClass):
    area = Area()
    area_show = Area()

    _items: list = []

    @staticmethod
    def set_mode(mode: int, width: int, height: int) -> None:
        """! Set the mode for inventory display. This can be attached to the
        bottom, top, left, or right, with a custom-set size.

        @param width How much space is available for the inventory. This is
            horizontal on top/bottom, vertical on left/right.
        @param height How far the inventory sticks out of the attached side of
            the screen.
        """
        show_scale = 0.1

        # set position relative to side
        if mode is INVENTORY_BOTTOM:
            Inventory.area.y = 1.0 - height
        elif mode is INVENTORY_TOP:
            Inventory.area.y = 0
        elif mode is INVENTORY_LEFT:
            Inventory.area.x = 0
        elif mode is INVENTORY_RIGHT:
            Inventory.area.x = 1.0 - height
        else:
            raise Exception(f"Unknown inventory mode {mode}")

        # center, set size, and set shower size
        if mode is INVENTORY_BOTTOM or mode is INVENTORY_TOP:
            Inventory.area.x = (1.0 - width) * 0.5
            Inventory.area.width = width
            Inventory.area.height = height
            Inventory.area_show = Area(Inventory.area)
            Inventory.area_show.height *= show_scale
        elif mode is INVENTORY_LEFT or mode is INVENTORY_RIGHT:
            Inventory.area.y = (1.0 - width) * 0.5
            Inventory.area.width = height
            Inventory.area.height = width
            Inventory.area_show = Area(Inventory.area)
            Inventory.area_show.width *= show_scale

        # correct position of shower if needed
        if mode is INVENTORY_RIGHT:
            Inventory.area_show.x = 1.0 - inventory_show_area.width
        elif mode is INVENTORY_BOTTOM:
            Inventory.area_show.y = 1.0 - inventory_show_area.height

        logging.info(f"set inventory mode to {mode} of size {width} X {height}")

    def add(item) -> None:
        if item in Inventory._items:
            #raise Exception(f"Tried to add '{item.name}' to inventory but it's already there")
            logging.warn(f"adding '{item.name}' to inventory but already there, ignoring")
            return
        
        item.remove_from_room()
        Inventory._items.append(item)

        logging.info(f"add '{item.name}' to inventory")

    def count() -> int:
        return len(Inventory._items)

    def clear() -> None:
        Inventory._items.clear()
        logging.info(f"clear inventory")

    def get(index: int) -> Item:
        if index < 0 or index >= len(Inventory._items):
            raise Exception(f"No item at index {index} in inventory")
        return Inventory._items[index]

    def remove(item: Item) -> None:
        if item not in Inventory._items:
            #raise Exception(f"Tried to remove '{item.name}' from inventory but it's not there")
            logging.warn(f"trying to remove '{item.name}' from inventory but not there, ignoring")
            return

        Inventory._items.remove(item)
        logging.info(f"remove '{item.name}' from inventory")

INVENTORY_ITEMS_PER_ROW = 4

INVENTORY_BOTTOM = 1
INVENTORY_LEFT = 2
INVENTORY_RIGHT = 3
INVENTORY_TOP = 4