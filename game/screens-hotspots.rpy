init python:
    def can_click():
        no_click_screens = [ "say", "Inventory" ]
        for screen_name in no_click_screens:
            if renpy.get_screen(screen_name):
                return False
        return True

init python:
    def hotspot_click_left(hs, x, y):
        left, right, top, bottom = hs.get_lrtb() 
        logging.debug(f"click at ({x}, {y}) checking vs ({left}, {top}) to ({right}, {bottom})")
        if x < left or x > right or y < top or y > bottom:
            return
        if Action.current is None:
            logging.info(f"left click hotspot '{hs.name}' with default action")
            Action.default.execute(hs)
            return
        logging.info(f"left click hotspot '{hs.name}' with current action {Action.current.name}")
        Action.current.execute(hs)

label click_left():
    $ logging.info("left click detected")
    if not can_click():
        $ logging.info("left click disallowed")
        return
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
    key "mouseup_1" action Call("click_left")
    #key "mouseup_2" action Jump("click_middle")
    #key "mouseup_3" action Jump("click_right")

label hotspot_hover(hs):
    $ hs.is_hovered = True
    return

label hotspot_unhover(hs):
    $ hs.is_hovered = False
    return

# TODO rename to HotspotRenderer
screen Hotspots():
    if Game.current_room is not None:
        zorder ZORDER_HOTSPOTS
        for hs in Game.current_room.hotspots:
            frame area (hs.x, hs.y, hs.width, hs.height):
                if hs.get_img_path() is None:
                    if DEBUG_SHOW_HOTSPOTS:
                        background "#F0F3"
                else:
                    background hs.get_img_path() 
            #mousearea area (hs.x, hs.y, hs.width, hs.height):
                #hovered Call("hotspot_hover", hs)
                #unhovered Call("hotspot_unhover", hs)