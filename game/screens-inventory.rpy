init python:
    inventory = []

    def inventory_add(item):
        #renpy.notify(f"You take {item.name}.")
        inventory.append(item)

    def inventory_use(item_index):
        if(item_index >= len(inventory)):
            return
        
        renpy.notify(f"Use {item_index} on what?")

label click(hs):
    $ hs.on_click()
    return

# TODO refactor => inventory_hide
label hide_inventory():
    $ renpy.notify("Hide inventory")
    hide screen Inventory
    show screen InventoryShower
    return

# TODO refactor => inventory_show
label show_inventory():
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
            unhovered Call("hide_inventory")
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
                    # TODO how to get this to animate sliding out like a drawer?
                    Call("show_inventory")
                ])

label describe_room:
    call hide_inventory
    "[current_room.desc]"
    return

label describe_equipped:
    call hide_inventory
    "[active_item.name]"
    return

screen Fullscreen():
    fixed:
        # left click - hide the invnetory, in addition to reacting to a hotspot
        key "mousedown_1" action Call("hide_inventory")

        # middle click - describe the equipped item, or the room if there is nont
        key "mousedown_2" action If(active_item is None, Call("describe_room"), Call("describe_equipped"))

        # right click - clear equipped if there is one, otherwise allow pass-through for describing hotspot
        key "mousedown_3" action If(active_item is None, None, Call("clear_equipped"))
