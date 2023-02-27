# Ren'PaC: Ren'Py Point and Click System

## Standards

- keep rpy as rpy and py as py
    - if a large chunk of python is necessary (such as a class), write it in pure python (do not call renpy methods)
    - if renpy methods are required from python, call the python from renpy and react accordingly with renpy in renpy

## To Do

### Main Iteration

- add logging to all normal actions
    - inventory changes
    - hotspot activation
    - room change
- items in items (containers, like bags and chests etc.)
    - how to handle open?
- how to distinguish between "use item" and "equip item for use on a hotspot" ?
- visual display of selected inventory item (for now just a text box with name, but later make cursors?)
- instead of show/hide on inventory / show inventory, would it be better to use an if? can put both in one screen
- visual display for items in inventory (use imagebuttons instead of buttons, how to resize? seems they ignore sizing)
- left click on screen where there's no item to see description of room
- right click on item to get description? or "use" on a specific place, like a corner icon?
- use items on other items (both must be in inventory? or this is conditional?)
- music areas: every room is in an area, which has a music setting which changes (smooth fade) on transition into different area
- menu button in corner (so we can handle mouse only)
- disable all keyboard controls (for mouse only jam)
- play sound for hotspot clicked or item use combination triggered
- disable interaction with hotspots while the (dialog) window is visible (since inventory doesn't refresh properly until it's gone)
    - alternatively, disallow showing of inventory while window is visible

- custom notify that allows multiple stacking messages 
- update text display in upper left for hovered item 
    (i.e. "use gruel on..." becomes "use gruel on shackles" or "use gruel on stairs down")

### Cool Ideas

- create generator for room hotspots so we can set the number in a config? or is there a way to make this unlimited?

### Wishlist

- randomize game using randomizer script on generation
- support drag and drop (either simultaneously, as a user option, or as a developer option)
- can we handle invert color for hover images with a script? (at the very least, generate with image-magick)
- visual editor to place items which generates a renpac script file