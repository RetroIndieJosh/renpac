init python:
    inventory = []

    def inventory_add(item):
        renpy.notify(f"You take {item.name}.")
        inventory.append(item)

    def inventory_use(item_index):
        if(item_index >= len(inventory)):
            return
        
        renpy.notify(f"Use {item_index} on what?")