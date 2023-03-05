init python:
    NO_CLICK_SCREENS = [ "say" ]

    def can_hover():
        for screen_name in NO_CLICK_SCREENS:
            if renpy.get_screen(screen_name):
                return False
        return True

    def pre_click():
        for screen_name in NO_CLICK_SCREENS:
            if renpy.get_screen(screen_name):
                renpy.hide_screen(screen_name)

    def hotspot_click_left(hs, x, y):
        #logging.debug(f"click at ({x}, {y}) checking vs {hs.rect}")
        if not hs.rect.contains(x, y):
            return
        if Item.selection_get() is not None:
            logging.info(f"left click hotspot '{hs.name}' with active item '{Item.selection_get().name}'")
            Action.get("use").execute(hs)
            return
        if Action.current is None:
            if Action.default is None:
                logging.info(f"left click hotspot '{hs.name}' but no current or default action, so do nothing")
            else:
                logging.info(f"left click hotspot '{hs.name}' with default action")
                Action.default.execute(hs)
            return
        logging.info(f"left click hotspot '{hs.name}' with current action {Action.current.name}")
        Action.current.execute(hs)

label click_left():
    #$ logging.debug("left click detected")
    python:
        Hotspot.hover_clear()
        x, y = renpy.get_mouse_pos()
        for hs in Room.current.hotspots:
            hotspot_click_left(hs, x, y) 
    return

label hotspot_click_right(hs):
    $ logging.info(f"right click hotspot '{hs.name}'")
    if hs.action_right is not None:
        $ hs.action_right.execute(hs)
    return

label hotspot_click_middle(hs):
    $ logging.info(f"middle click hotspot '{hs.name}'")
    if hs.action_middle is not None:
        $ hs.action_middle.execute(hs)
    return

label hotspot_describe(hs):
    "[hs.desc]"
    return

screen ClickArea():
    if not inventory_visible and renpy.get_screen("say") is None:
        #key "mouseup_1" action If(can_click(), Call("click_left"), None)
        key "mouseup_1" action [pre_click, Call("click_left")]
        #key "mouseup_2" action Jump("click_middle")
        #key "mouseup_3" action Jump("click_right")

label hotspot_hover(hs):
    $ Hotspot.hover_set(hs)
    return

label hotspot_unhover(hs):
    $ Hotspot.hover_clear()
    return

screen Hotspots():
    if Room.current is not None:
        zorder ZORDER_HOTSPOTS
        $ Room.current.clear_deleted()
        for hs in Room.current.hotspots:
            $ x, y, width, height = hs.rect.get_xywh()
            if DEBUG_SHOW_HOTSPOTS:
                frame:
                    area (x, y, width, height)
                    if hs.is_hovered:
                        background "#F0FA"
                    else:
                        background "#F0F3"
            frame:
                area (x, y, width, height)
                background hs.get_img_path() 
            mousearea:
                area (x, y, width, height)
                hovered If(can_hover(), Call("hotspot_hover", hs), None)
                unhovered If(can_hover(), Call("hotspot_unhover", hs), None)