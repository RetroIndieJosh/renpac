# RenPaC: Ren'Py Point and Click Engine

(c)2023 Joshua D. McLean, All Rights Reserved

A system for developing point & click adventures in the Macventure or Sierra
style using the power of [Ren'Py](https://www.renpy.org/).

The user is presented with a room populated by clickable hotspots. Developer
configurable actions apply to these hotspots to manipulate the world.
Specialized hotspots include items and exits.

## RenPaC Structure

**Ren'py Python Generator**: A tool to convert raw .py files into .rpy files
which are ordered by priority to handle dependencies among the Python scripts
since Ren'py only knows about symbols previously read.

**RenPaC Base**: Base Python files shared between Engine and Builder. These will
both be utilized by the Builder during developement *and* copied to ship on a
build alongside the Engine.

**RenPaC Engine**: Script files to be compiled into Ren'py and copied to run a
RenPaC game.

**RenPaC Builder**: A tool which takes a build configuration and game
configuration to create a game by copying necessary files from the RenPaC
engine along with a generated .game.rpy game definition script.

**Build Configuration**: Defines properties used during building of the game,
such as debug configuration and paths.

**Game Configuration**: Defines the setup of a specific game: rooms, items, etc.

**RenPaC Editor** (forthcoming): A visual editor to set up rooms and place
items, plus an IDE for RenPaC game configuration files.

## Builder

Tools and scripts for converting a RenPaC .cfg file into a playable Ren'py game readable by the RenPaC engine.

The builder.cfg sets up the build giving a path to the renpac-engine directory (taken from GitHub) and the game definition .cfg file.

Run build.py to generate the game. This will:

1. convert the game .cfg file to a .game.renpy file
1. collect all resources defined by the game .cfg into the relevant directories (game/audio, game/images, etc.)
1. copy the necessary build files from renpac-engine
1. create a folder named after the game containing all necessary Ren'py files
