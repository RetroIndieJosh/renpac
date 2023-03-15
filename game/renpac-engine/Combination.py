from dataclasses import dataclass

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