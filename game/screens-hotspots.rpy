init python:
    def can_click():
        # TODO some way to set up a list of these for customization
        no_click_screens = [ "say", "Inventory" ]
        for screen in no_click_screens:
            if renpy.get_screen(no_click_screens):
                return False
        return True

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
            else:
                imagebutton:
                    auto hs.img_path 
                    action If(can_click(), [
                        Hide(), 
                        Call("click", hs)
                    ], None)
