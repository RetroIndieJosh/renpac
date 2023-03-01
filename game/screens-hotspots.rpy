init python:
    def can_click():
        no_click_screens = [ "say", "Inventory" ]
        for screen_name in no_click_screens:
            if renpy.get_screen(screen_name):
                return False
        return True

label hotspot_click_left(hs):
    if Action.current is None:
        $ logging.info(f"left-clicked hotspot '{hs.name}' with no current action")
        if hs.action_left is not None:
            $ hs.action_left.execute(hs)
        return
    # TODO do actions have names? if not, they should
    $ logging.info(f"left-clicked hotspot '{hs.name}' with current {Action.current.name}")
    $ Action.current.execute(hs)
    return

label hotspot_click_right(hs):
    $ logging.info(f"right-clicked hotspot '{hs.name}'")
    if hs.action_right is not None:
        $ hs.action_right.execute(hs)
    return

label hotspot_click_middle(hs):
    $ logging.info(f"middle-clicked hotspot '{hs.name}'")
    if hs.action_middle is not None:
        $ hs.action_middle.execute(hs)
    return

label hotspot_describe(hs):
    "[hs.desc]"
    return

screen Hotspots(hotspots):
    zorder ZORDER_HOTSPOTS
    for hs in hotspots:
        vbox area (hs.x, hs.y, hs.width, hs.height):
            # TODO does this work? is it only acting in the hotspot?
            key "mousedown_3" action If(active_item is None, Call("hotspot_click_middle", hs), None)
            if hs.img_path is None:
                button:
                    if DEBUG_SHOW_HOTSPOTS:
                        background "#F0F3"
                    action If(can_click(), [
                        If(DEBUG_NOTIFY_HOTSPOTS, Notify(f"clicked '{hs.name}'"), None),
                            Hide(), 
                            Call("hotspot_click_left", hs)
                    ], None)
                    alternate If(active_item is None, Call("hotspot_click_right", hs), None)
            else:
                imagebutton:
                    auto hs.img_path 
                    action If(can_click(), [
                        Hide(), 
                        Call("hotspot_click_left", hs)
                    ], None)
                    alternate If(active_item is None, Call("hotspot_click_right", hs), None)
