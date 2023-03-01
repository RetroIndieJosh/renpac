from dataclasses import dataclass

@dataclass(frozen=True)
class Combination:
    func: function = None
    delete_self: bool = False
    delete_other: bool = False