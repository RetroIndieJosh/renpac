init python:
    def can_click():
        no_click_screens = [ "say", "Inventory" ]
        for screen_name in no_click_screens:
            if renpy.get_screen(screen_name):
                return False
        return True

label hotspot_click(hs):
    $ hs.click()
    return

label hotspot_describe(hs):
    "[hs.desc]"
    return

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
                            Call("hotspot_click", hs)
                    ], None)
                    alternate If(active_item is None, Call("hotspot_describe", hs), None)
            else:
                imagebutton:
                    auto hs.img_path 
                    action If(can_click(), [
                        Hide(), 
                        Call("hotspot_click", hs)
                    ], None)
                    alternate If(active_item is None, Call("hotspot_describe", hs), None)
