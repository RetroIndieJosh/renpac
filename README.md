# RenPaC: Ren'Py Point and Click System by Joshua McLean

(c)2023 Joshua D. McLean, All Rights Reserved

A system for developing point & click adventures in the Macventure or Sierra style using the power of [Ren'Py](https://www.renpy.org/).

The user is presented with a room populated by clickable hotspots. Developer configurable actions apply to these hotspots to manipulate the world. Specialized hotspots include items and exits.

Currently, the system is (meant to be) set up as follows:

- left click an Item => take or equip the item
- right click an Item => use the item

- left click an Exit => go to the target room 

- right click nothing with an item equipped => unequip the item
- right click a Hotspot with an item equipped => use the equipped item on the target

- middle click a Hotspot => describe the hotspot

The system also supports mousewheel down and up actions.