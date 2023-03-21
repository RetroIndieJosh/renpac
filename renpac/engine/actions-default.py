import logging

from renpac.engine.Action import Action
from renpac.engine.Exit import Exit
from renpac.engine.Hotspot import Hotspot
from renpac.engine.Inventory import Inventory
from renpac.engine.Item import Item
from renpac.engine.Renpac import Renpac
from renpac.engine.Room import Room

def action_examine(target: Hotspot) -> None:
    """! Action for looking at a hotspot (item or exit).
    
    @param target The hotspot the player is interacting with.
    """
    if target is None:
        Renpac.narrate(f"[Game.current_room.desc]")
    elif target.desc is None:
        Renpac.narrate(f"That's a {target.name}.")
    else:
        Renpac.narrate(f"{target.desc}")

def action_go(target: Hotspot) -> None:
    """! Action for going to a room through the target hotspot (exit). Fails if
    the target is not an exit.
    
    @param target The hotspot the player is interacting with.
    """
    if type(target) is Exit and target.target is not None:
        Room.current_set(target.target)
    else:
        Renpac.narrate("You can't go there.")

def action_go_allowed(target: Hotspot) -> bool:
    """! Whether the user is allowed to "go" on the given hotspot.
    
    @param target The hotspot the player is interacting with.
    """
    return target is not None and type(target) is Exit

def action_take(target: Hotspot) -> None:
    """! Action for going to a room through the target hotspot (exit). Fails if
    the target is not an item.
    
    @param target The hotspot the player is interacting with.
    """
    if target is None or type(target) is not Item or target.fixed:
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
    """! Whether the user is allowed to "take" on the given hotspot.
    
    @param target The hotspot the player is interacting with.
    """
    return target is not None and type(target) is Item and not target.fixed

def action_use(target: Hotspot) -> None:
    """! Action for using the selected item on the target hotspot. Fails if no
    item currently selected.
    
    @param target The hotspot the player is interacting with.
    """
    selection = Item.selection_get()
    if selection is None:
        return
    selection.use_on(target)
    
def left_click(target: Hotspot):
    """! Handle the player left clicking. Executes the highest-level allowed
    default action: take, go, or examine, in that order.
    
    @param target The hotspot the player is clicking.
    """
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