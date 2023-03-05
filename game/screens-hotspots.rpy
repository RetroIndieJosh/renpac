init python:
    NO_CLICK_SCREENS = [ "say", "Inventory" ]

    def can_hover():
        for screen_name in NO_CLICK_SCREENS:
            if renpy.get_screen(screen_name):
                logging.debug("hover blocked")
                return False
        return True

    def pre_click():
        for screen_name in NO_CLICK_SCREENS:
            if renpy.get_screen(screen_name):
                renpy.hide_screen(screen_name)

    def hotspot_click_left(hs, x, y):
        logging.debug(f"click at ({x}, {y}) checking vs {hs.rect}")
        if not hs.rect.contains(x, y):
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
    $ logging.info("left click detected")
    python:
        x, y = renpy.get_mouse_pos()
        for hs in Game.current_room.hotspots:
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
    #key "mouseup_1" action If(can_click(), Call("click_left"), None)
    key "mouseup_1" action [pre_click, Call("click_left")]
    #key "mouseup_2" action Jump("click_middle")
    #key "mouseup_3" action Jump("click_right")

label hotspot_hover(hs):
    $ Game.hover_set(hs)
    return

label hotspot_unhover(hs):
    $ Game.hover_clear()
    return

# TODO split hover into a second screen (HotspotsHover, HotspotsRender)
screen Hotspots():
    if Game.current_room is not None:
        zorder ZORDER_HOTSPOTS
        for hs in Game.current_room.hotspots:
            frame area (hs.rect.x, hs.rect.y, hs.rect.width, hs.rect.height):
                if hs.get_img_path() is None:
                    if DEBUG_SHOW_HOTSPOTS:
                        background "#F0F3"
                else:
                    background hs.get_img_path() 
            mousearea area (hs.rect.x, hs.rect.y, hs.rect.width, hs.rect.height):
                hovered If(can_hover(), Call("hotspot_hover", hs), None)
                unhovered If(can_hover(), Call("hotspot_unhover", hs), None)