init python:
    inventory = []

    def inventory_add(item):
        if item in inventory:
            raise Exception(f"Tried to add '{item.name}' to inventory but it's already there")
        renpy.notify(f"Got {item.name}.")
        inventory.append(item)

    def inventory_remove(item):
        renpy.notify(f"Lost {item.name}.")
        if item not in inventory:
            raise Exception(f"Tried to remove '{item.name}' from inventory but it's not there")
        inventory.remove(item)

    def inventory_use(item_index):
        if(item_index >= len(inventory)):
            return
        
        renpy.notify(f"Use {item_index} on what?")

label inventory_hide:
    $ renpy.notify("Hide inventory")
    hide screen Inventory
    show screen InventoryShower
    return

label inventory_show:
    $ renpy.notify("Show inventory")
    hide screen InventoryShower
    show screen Inventory
    return

init python:
    from math import ceil

screen Inventory():
    zorder ZORDER_INVENTORY
    frame:
        area (inventory_area.x, inventory_area.y, inventory_area.width, inventory_area.height)

        background "#0009"
        mousearea:
            unhovered Call("inventory_hide")
        vbox:
            $ global inventory
            for i in range(0, ceil(len(inventory) / INVENTORY_ITEMS_PER_ROW)):
                hbox:
                    for k in range(i * INVENTORY_ITEMS_PER_ROW, min(len(inventory), INVENTORY_ITEMS_PER_ROW * (i + 1))):
                        textbutton f"{inventory[k].name}":
                            action Call("equip_item", inventory[k])

screen InventoryShower():
    frame:
        area (inventory_show_area.x, inventory_show_area.y, inventory_show_area.width, inventory_show_area.height)

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
    fixed:
        # left click - hide the invnetory, in addition to reacting to a hotspot
        key "mousedown_1" action Call("inventory_hide")

        # middle click - describe the equipped item, or the room if there is nont
        key "mousedown_2" action If(active_item is None, Call("describe_room"), Call("describe_equipped"))

        # right click - clear equipped if there is one, otherwise allow pass-through for describing hotspot
        key "mousedown_3" action If(active_item is None, None, Call("clear_equipped"))
