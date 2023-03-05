import logging

from . import Action, Exit, Hotspot, Inventory, Item, Renpac, Room

def action_examine(target: Hotspot) -> None:
    if target is None:
        Renpac.narrate(f"[Game.current_room.desc]")
    elif target.desc is None:
        Renpac.narrate(f"That's a {target.name}.")
    else:
        Renpac.narrate(f"{target.desc}")

def action_go(target: Hotspot) -> None:
    if not action_go_allowed(target):
        Renpac.narrate("You can't go there.")
    Room.current_set(target.target)

def action_go_allowed(target: Hotspot) -> bool:
    return target is not None and type(target) is Exit

def action_take(target: Hotspot) -> None:
    if not action_take_allowed(target):
        Renpac.narrate("You can't take that.")
        return
    Inventory.add(target)
    if target.is_hovered:
        Hotspot.hover_clear()
    if target.take_message is None:
        Renpac.narrate(f"You take {target.name}.")
    else:
        Renpac.narrate(target.take_message)

def action_take_allowed(target: Hotspot) -> bool:
    return target is not None and type(target) is Item and target.fixed is False

def action_use(target: Hotspot) -> None:
    selection = Item.selection_get()
    # use only makes sense if we have something to use *on* the target
    if selection is None:
        return
    selection.use_on(target)
    

def left_click(target: Hotspot):
    if action_take_allowed(target):
        logging.debug("take action")
        action_take(target)
        return

    if action_go_allowed(target):
        logging.debug("go action")
        action_go(target)
        return

    logging.debug("examine action")
    action_examine(target)

Action(None, left_click)
Action("examine", action_examine)
Action("go", action_go)
Action("take", action_take)
Action("use", action_use)

Action.lock()