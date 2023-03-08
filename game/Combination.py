from dataclasses import dataclass

TARGET_NONE = 0b00
TARGET_SELF = 0b01
TARGET_OTHER = 0b10

@dataclass(frozen=True)
class Combination:
    message: str
    delete_flags: int
    replace_flags: int
    replace_with: object