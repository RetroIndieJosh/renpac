init python:
    from math import ceil
    inventory_visible = False

label inventory_hide():
    $ inventory_visible = False
    return

label inventory_show():
    $ inventory_visible = True
    return

screen InventoryScreen():
    zorder ZORDER_INVENTORY
    $ Inventory.clear_deleted()
    $ x, y, width, height = Inventory.rect.get_xywh()
  
    if can_hover():
        mousearea:
            area (x, y, width, height)
            if inventory_visible:
                unhovered Call("inventory_hide")
            else:
                hovered Call("inventory_show")

    frame:
        area (x, y, width, height)

        if inventory_visible:
            background "#FFF3"
        else:
            background "#0000"

        if inventory_visible:
            vbox:
                $ item_count = Inventory.count()
                for i in range(0, ceil(item_count / INVENTORY_ITEMS_PER_ROW)):
                    hbox:
                        for k in range(i * INVENTORY_ITEMS_PER_ROW, min(item_count, INVENTORY_ITEMS_PER_ROW * (i + 1))):
                            $ item = Inventory.get(k)
                            imagebutton:
                                # TODO reset item to hover = False on take so this gets the right one
                                idle item.get_img_path()
                                action Call("equip_item", item)

    if inventory_visible:
        $ center_x, center_y = Inventory.rect.get_center()
        text "Inventory":
            xcenter center_x
            ycenter center_y
            color "#FFF6"
        