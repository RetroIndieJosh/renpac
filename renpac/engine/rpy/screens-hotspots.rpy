init python:
    def hotspot_click_left(hs):
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
    if not Renpac.can_hover():
        return
    python:
        target = Hotspot.hover_get()
        if target is not None:
            hotspot_click_left(Hotspot.hover_get())
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
    if not inventory_visible and Renpac.can_hover():
        key "mouseup_1" action Call("click_left")
        #key "mouseup_2" action Jump("click_middle")
        #key "mouseup_3" action Jump("click_right")

label hotspot_hover(hs):
    $ Hotspot.hover_set(hs)
    "[hs.desc]"
    return

label hotspot_unhover(hs):
    $ Hotspot.hover_clear()
    "[Room.current.desc]"
    return

screen Hotspots():
    if Room.current is not None:
        zorder ZORDER_HOTSPOTS
        $ Room.current.clear_deleted()
        for hs in Room.current.hotspots:
            $ img = hs.get_img_path()
            $ x, y, width, height = hs.rect.get_xywh()
            if DEBUG_SHOW_HOTSPOTS:
                frame:
                    area (x, y, width, height)
                    if hs.is_hovered:
                        background "#F0FA"
                    else:
                        background "#F0F3"
            if img is not None:
                frame:
                    area (x, y, width, height)
                    background img
            mousearea:
                area (x, y, width, height)
                hovered If(Renpac.can_hover(), Call("hotspot_hover", hs), None)
                unhovered If(Renpac.can_hover(), Call("hotspot_unhover", hs), None)