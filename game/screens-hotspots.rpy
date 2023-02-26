init python:
    def can_click():
        # TODO some way to set up a list of these for customization
        no_click_screens = [ "say", "Inventory" ]
        for screen_name in no_click_screens:
            if renpy.get_screen(screen_name):
                return False
        return True

init python:
    def hotspot_delete(hs):
        if hs in inventory:
            inventory.remove(hs)
        elif hs.room is not None:
            hs.room.remove_hotspot(hs)
        else:
            raise Exception(f"Tried to delete hotspot '{hs.name}' but it doesn't exist in inventory or room!")

    def hotspot_click(hs):
        global active_item

        if active_item is None:
            hs.on_click()
            return

        combo = hs.combine(active_item)
        if combo is None:
            renpy.say(None, f"You can't use {active_item.name} on {hs.name}!")
            return

        renpy.say(None, f"You use {active_item.name} on {hs.name}")
        # TODO is it not calling this?
        combo.func()
        if(combo.remove_self):
            hotspot_delete(active_item)
            active_item = None
        else:
            hotspot_delete(hs)
        active_item = None

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
