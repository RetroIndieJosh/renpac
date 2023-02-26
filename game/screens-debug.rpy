screen Debug():
    fixed:
        if renpy.get_screen("say"):
            text "The say screen is showing."
        else:
            text "The say screen is hidden."