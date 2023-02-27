init python:
    # TODO is there a way to move this to Hotspot.py?
    def can_click():
        no_click_screens = [ "say", "Inventory" ]
        for screen_name in no_click_screens:
            if renpy.get_screen(screen_name):
                return False
        return True

# TODO refactor => hotspot_click
label click(hs):
    $ hs.click()
    return

# TODO move to Hotspot.describe()
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
