init python:
    def can_click():
        no_click_screens = [ "say", "Inventory" ]
        for screen_name in no_click_screens:
            if renpy.get_screen(screen_name):
                return False
        return True

init python:
    def hotspot_delete(hs):
        logging.info(f"delete hotspot {hs.name}")
        if hs in inventory:
            inventory.remove(hs)
        elif hs.room is not None:
            hs.room.remove_hotspot(hs)
        else:
            raise Exception(f"Tried to delete hotspot '{hs.name}' but it doesn't exist in inventory or room!")

    def hotspot_click(hs):
        global active_item

        if active_item is None:
            logging.debug(f"no active item, do regular click on hotspot {hs.name}")
            hs.on_click()
            return

        logging.debug(f"active item is {active_item.name}, try {hs.name}.combine({active_item.name})")
        combo = hs.combine(active_item)
        if combo is None:
            logging.info(f"cannot combine {active_item.name} on {hs.name}")
            renpy.say(None, f"You can't use {active_item.name} on {hs.name}!")
            return

        if combo.delete_self:
            logging.debug(f"remove self ({active_item.name})")
            hotspot_delete(active_item)
        if combo.delete_target:
            logging.debug(f"remove target ({hs.name})")
            hotspot_delete(hs)

        active_item = None

        # do func last in case it includes an execution-ender such as renpy.say()
        if combo.func is not None:
            combo.func()

label click(hs):
    $ hotspot_click(hs)
    return

label describe_hotspot(hs):
    "[hs.desc]"
    return

# TODO some kind of lint to check for overlapping hotspots (warn)
screen Hotspots(hotspots):
    zorder ZORDER_HOTSPOTS
    for hs in hotspots:
        vbox area (hs.x, hs.y, hs.width, hs.height):
            if hs.img_path is None:
                button:
                    if DEBUG_SHOW_HOTSPOTS:
                        background "#F0F3"
                    action If(can_click(), [
                        If(DEBUG_NOTIFY_HOTSPOTS, Notify(f"clicked '{hs.name}'"), None),
                            Hide(), 
                            Call("click", hs)
                    ], None)
                    alternate If(active_item is None, Call("describe_hotspot", hs), None)
            else:
                imagebutton:
                    auto hs.img_path 
                    action If(can_click(), [
                        Hide(), 
                        Call("click", hs)
                    ], None)
                    alternate If(active_item is None, Call("describe_hotspot", hs), None)
