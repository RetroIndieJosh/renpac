# Notes

## To Do

### Main Iteration

- instead of Room setting up the hotspots, have only the DATA for the hotspots contained therein
    - and have Game do the actual creation of hotspots (can we do this in rpy instead of py?)
- visual display of selected inventory item (for now just a text box with name, but later make cursors?)
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

### Cool Ideas

- create generator for room hotspots so we can set the number in a config? or is there a way to make this unlimited?

### Wishlist

- randomize game using randomizer script on generation
- support drag and drop (either simultaneously, as a user option, or as a developer option)
- can we handle invert color for hover images with a script? (at the very least, generate with image-magick)