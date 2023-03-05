import logging

from . import Item, Rect, StaticClass

INVENTORY_ITEMS_PER_ROW = 4

INVENTORY_BOTTOM = 1
INVENTORY_LEFT = 2
INVENTORY_RIGHT = 3
INVENTORY_TOP = 4

class Inventory(StaticClass):
    rect = Rect()
    rect_show = Rect()

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

    def clear_deleted() -> None:
        Inventory._items = [item for item in Inventory._items if not item.is_deleted()]

    def get(index: int) -> Item:
        if index < 0 or index >= len(Inventory._items):
            raise Exception(f"No item at index {index} in inventory")
        return Inventory._items[index]

    def has(item: Item) -> bool:
        return item in Inventory._items

    def remove(item: Item) -> None:
        if item not in Inventory._items:
            #raise Exception(f"Tried to remove '{item.name}' from inventory but it's not there")
            logging.warn(f"trying to remove '{item.name}' from inventory but not there, ignoring")
            return

        Inventory._items.remove(item)
        logging.info(f"remove '{item.name}' from inventory")
