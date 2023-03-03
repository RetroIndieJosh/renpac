import logging

from . import Action, Area, Hotspot, Item, Renpac, StaticClass

def action_take(item: Hotspot):
    if type(item) is not Item:
        Renpac.say("You can't take that.")
    else:
        Inventory.add(item)
    renpy.block_rollback() #type: ignore

Action.register("take", action_take)

class Inventory(StaticClass):
    _items: list = []

    def add(item) -> None:
        if item in Inventory._items:
            raise Exception(f"Tried to add '{item.name}' to inventory but it's already there")
        
        item.remove_from_room()
        Inventory._items.append(item)

        Renpac.notify(f"Got {item.name}.")
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
            raise Exception(f"Tried to remove '{item.name}' from inventory but it's not there")
        Inventory._items.remove(item)

        Renpac.notify(f"Lost {item.name}.")
        logging.info(f"remove '{item.name}' from inventory")

INVENTORY_ITEMS_PER_ROW = 4

INVENTORY_BOTTOM = 1
INVENTORY_LEFT = 2
INVENTORY_RIGHT = 3
INVENTORY_TOP = 4

inventory_area = Area() # type: ignore
inventory_show_area = Area() # type: ignore

# TODO move to class above
# width is how much space is available for the inventory (horizontal on top/bottom, vertical on left/right)
# height is how far the inventory widthes out of the attached side of the screen
def set_inventory_mode(mode: int, width: int, height: int) -> None:
    global inventory_area, inventory_show_area

    show_scale = 0.1

    # set position relative to side
    if mode is INVENTORY_BOTTOM:
        inventory_area.y = 1.0 - height
    elif mode is INVENTORY_TOP:
        inventory_area.y = 0
    elif mode is INVENTORY_LEFT:
        inventory_area.x = 0
    elif mode is INVENTORY_RIGHT:
        inventory_area.x = 1.0 - height
    else:
        raise Exception(f"Unknown inventory mode {mode}")

    # center, set size, and set shower size
    if mode is INVENTORY_BOTTOM or mode is INVENTORY_TOP:
        inventory_area.x = (1.0 - width) * 0.5
        inventory_area.width = width
        inventory_area.height = height
        inventory_show_area = Area(inventory_area)
        inventory_show_area.height *= show_scale
    elif mode is INVENTORY_LEFT or mode is INVENTORY_RIGHT:
        inventory_area.y = (1.0 - width) * 0.5
        inventory_area.width = height
        inventory_area.height = width
        inventory_show_area = Area(inventory_area)
        inventory_show_area.width *= show_scale

    # correct position of shower if needed
    if mode is INVENTORY_RIGHT:
        inventory_show_area.x = 1.0 - inventory_show_area.width
    elif mode is INVENTORY_BOTTOM:
        inventory_show_area.y = 1.0 - inventory_show_area.height

    logging.info(f"set inventory mode to {mode} of size {width}x{height}")

