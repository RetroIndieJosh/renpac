# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#define e = Character("Eileen")

label start:
    $ init_game()

    while True:
        window hide
        pause

    return

label take_item(item):
    "You take [item.name]."
    $ item.take()
    return
