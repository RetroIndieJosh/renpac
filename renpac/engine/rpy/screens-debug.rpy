init python:
    def hover_name():
        hover = Hotspot.hover_get()
        if hover is None:
            return "(None)"
        return hover.name

screen Debug():
    frame:
        xpos 0
        ypos 0
        text hover_name()