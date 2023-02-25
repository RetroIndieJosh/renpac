# Notes

## Layout

- inventory pops up from top, bottom, left, or right when an invisible one-pixel line gets hovered
- player clicks an item to collect it
- player clicks an item from inventory to select, then click an area on the screen to use it there
- use `while true: wait` to allow unlimited in-game mouse clicks without showing dialogue
- clicking room anywhere there isn't an item without an item selected shows description
- right-clicking an item shows description ?

## Ideas

- generate game for InventoryItem1, 2, etc. from a config file (InventoryMax = 10, RoomMaxItems = 10, etc.)
- generate game from special script defining rooms and items like a text adventure
- randomize game using randomizer script on generation
- should it also support drag + drop for items? can it do both?
- can we make a script to handle generation of invert-color for hover images? (maybe use image-magick?)

- instead of items, create hotspots with events: get item, change room, etc.