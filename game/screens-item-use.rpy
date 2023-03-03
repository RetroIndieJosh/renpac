init python:
    active_item = None

label clear_equipped:
    call inventory_hide
    python:
        global active_item
        active_item = None
        logging.info("clear active item")
    return

label equip_item(item):
    call inventory_hide
    python:
        active_item = item
        logging.info(f"set active item to '{active_item.name if active_item else 'None'}'")
    return

screen Equipped():
    frame:
        if active_item is None:
            area (0, 0, 0, 0)
        else:
            background "#0008"
            text f"use {active_item.name} on..."