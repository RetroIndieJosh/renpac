# RenPaC Builder

(c)2023 Joshua D McLean, All Rights Reserved

Tools and scripts for converting a RenPaC .cfg file into a playable Ren'py game readable by the RenPaC engine.

The builder.cfg sets up the build giving a path to the renpac-engine directory (taken from GitHub) and the game definition .cfg file.

Run build.py to generate the game. This will:

1. convert the game .cfg file to a .game.renpy file
1. collect all resources defined by the game .cfg into the relevant directories (game/audio, game/images, etc.)
1. copy the necessary build files from renpac-engine
1. create a folder named after the game containing all necessary Ren'py files
