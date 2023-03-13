from dataclasses import dataclass

## Flag for no target
TARGET_NONE = 0b00

## Flag for targeting the selected item (the one the player is using on a target hotspot)
TARGET_SELF = 0b01

## Flag for targeting the target item (the hotspot the player "uses" the selected item on)
TARGET_OTHER = 0b10

@dataclass(frozen=True)
class Combination:
    """! Specification for handling the combination of two items.
    """

    ## The message to display when the combination occurs
    message: str

    ## What to delete when the combination occurs (see TARGET_ flags)
    delete_flags: int

    ## What to replace when the combination occurs (see TARGET_ flags)
    replace_flags: int

    ## The Item to replace the item specified in replace_flags with (must be an
    ## Item, but no type hinting here to avoid circular dependencies)
    replace_with: object