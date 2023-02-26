label clear_equipped:
    python:
        global active_item
        active_item = None
        renpy.notify("equipped item cleared")
    return

label equip_item(item):
    call hide_inventory()
    python:
        active_item = item
        renpy.notify(f"equipped {item.name}")
    return
