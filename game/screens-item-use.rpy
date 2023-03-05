label clear_equipped:
    call inventory_hide
    python:
        Item.selection_clear()
        logging.info("clear active item")
    return

label equip_item(item):
    call inventory_hide
    python:
        Item.selection_set(item)
    return

screen Equipped():
    $ selected = Item.selection_get()
    frame:
        if selected is None:
            area (0, 0, 0, 0)
        else:
            background "#0008"
            text f"use {selected.name} on..."