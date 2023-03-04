label inventory_hide:
    hide screen Inventory
    show screen InventoryShower
    return

label inventory_show:
    hide screen InventoryShower
    show screen Inventory
    return

init python:
    from math import ceil

screen Inventory():
    zorder ZORDER_INVENTORY
    frame:
        area (Inventory.area.x, Inventory.area.y, Inventory.area.width, Inventory.area.height)

        background "#0009"
        mousearea:
            unhovered Call("inventory_hide")
        vbox:
            $ item_count = Inventory.count()
            for i in range(0, ceil(item_count / INVENTORY_ITEMS_PER_ROW)):
                hbox:
                    for k in range(i * INVENTORY_ITEMS_PER_ROW, min(item_count, INVENTORY_ITEMS_PER_ROW * (i + 1))):
                        textbutton f"{Inventory.get(k).name}":
                            action Call("equip_item", Inventory.get(k))

screen InventoryShower():
    frame:
        area (Inventory.area_show.x, Inventory.area_show.y, Inventory.area_show.width, Inventory.area_show.height)

        if DEBUG_INVENTORY_SHOWER:
                background "#F0F"

        mousearea:
            # don't show inventory if the dialogue window is showing
            hovered If(renpy.get_screen("say"), None, [
                    Call("inventory_show")
                ])

label describe_room:
    call inventory_hide
    "[Game.current_room.desc]"
    return

label describe_equipped:
    call inventory_hide
    "[active_item.name]"
    return

screen Fullscreen():
    null
    #fixed:
        # left click - hide the invnetory, in addition to reacting to a hotspot
        #key "mousedown_1" action Call("inventory_hide")

        # middle click - describe the equipped item, or the room if there is nont
        #key "mousedown_2" action If(active_item is None, Call("describe_room"), Call("describe_equipped"))

        # right click - clear equipped if there is one, otherwise allow pass-through for describing hotspot
        #key "mousedown_3" action If(active_item is None, None, Call("clear_equipped"))
