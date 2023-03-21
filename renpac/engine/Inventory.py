import logging

from renpac.base.StaticClass import StaticClass

from renpac.engine.Item import Item
from renpac.engine.Rect import Rect

## THe number of items to show per row in the inventory (which becomes columns
## if the inventory is anchored to the left or right)
INVENTORY_ITEMS_PER_ROW = 4

## Anchor the inventory to the bottom of the screen
INVENTORY_BOTTOM = 1

## Anchor the inventory to the left of the screen
INVENTORY_LEFT = 2

## Anchor the inventory to the right of the screen
INVENTORY_RIGHT = 3

## Anchor the inventory to the top of the screen
INVENTORY_TOP = 4

class Inventory(StaticClass):
    """! A collection of items held by the player
    """

    # TODO make private
    ## The rectangle where the inventory is drawn
    rect = Rect()

    ## The list of items in the inventory
    _items: list = []

    @staticmethod
    def set_mode(mode: int, length: int, depth: int) -> None:
        """! Set the mode for inventory display. This can be attached to the
        bottom, top, left, or right, with a custom-set size.

        @param length How much space is available for the inventory. This is
            horizontal on top/bottom, vertical on left/right.
        @param depth How far the inventory sticks out of the attached side of
            the screen.
        """
        logging.info(f"set inventory mode {mode}, size {length} x {depth}")

        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080

        # set position relative to side
        if mode is INVENTORY_TOP or mode is INVENTORY_LEFT:
            Inventory.rect.set_pos(0, 0)
        elif mode is INVENTORY_BOTTOM:
            Inventory.rect.set_pos(0, SCREEN_HEIGHT - depth)
        elif mode is INVENTORY_RIGHT:
            Inventory.rect.set_pos(SCREEN_WIDTH - depth, 0)
        else:
            raise Exception(f"Unknown inventory mode {mode}")

        # set size and center along side
        if mode is INVENTORY_BOTTOM or mode is INVENTORY_TOP:
            Inventory.rect.set_size(length, depth)
            Inventory.rect.center_hori(1920)
        elif mode is INVENTORY_LEFT or mode is INVENTORY_RIGHT:
            Inventory.rect.set_size(depth, length)
            Inventory.rect.center_vert(1080)

        logging.info(f"inventory viewer created with area {Inventory.rect}")

    @staticmethod
    def add(item: Item) -> None:
        """! Add an item to the inventory, first removing it from the current
        location. Raise a warning if the item is already in the inventory.

        @param item The item to add
        """
        if item in Inventory._items:
            #raise Exception(f"Tried to add '{item.name}' to inventory but it's already there")
            logging.warn(f"adding '{item.name}' to inventory but already there, ignoring")
            return
        
        item.remove_from_room()
        Inventory._items.append(item)

        logging.info(f"add '{item.name}' to inventory")

    @staticmethod
    def count() -> int:
        """! Get the number of items in the inventory.
        
        @return The number of items in the inventory, an integer
        """
        return len(Inventory._items)

    @staticmethod
    def clear() -> None:
        """! Clear all items from the inventory
        """
        Inventory._items.clear()
        logging.info(f"clear inventory")

    @staticmethod
    def clear_deleted() -> None:
        """! Clear any deleted items from the inventory
        """
        Inventory._items = [item for item in Inventory._items if not item.is_deleted()]

    @staticmethod
    def get(index: int) -> Item:
        """! Get the inventory item at the given index. If the index is invalid
        for the inventory, raise an exception.
        
        @param index The 0-based index of the item to get

        @return The Item at the given index
        """
        if index < 0 or index >= len(Inventory._items):
            raise Exception(f"No item at index {index} in inventory")
        return Inventory._items[index]

    @staticmethod
    def has(item: Item) -> bool:
        """! Determine whether the given item is in the inventory
        
        @param item The item to check for
        
        @return True if the item is in the inventory, False otherwise
        """
        return item in Inventory._items

    @staticmethod
    def remove(item: Item) -> None:
        """! Remove the given item from the inventory. Warn if the item is not
        in the inventory.
        
        @param item The item to remove
        """
        if item not in Inventory._items:
            logging.warn(f"trying to remove '{item.name}' from inventory but not there, ignoring")
            return

        Inventory._items.remove(item)
        logging.info(f"remove '{item.name}' from inventory")
