# TODO this is just a data class, can we make a struct? (named tuple?)
class Combination:
    def __init__(self) -> None:
        self.func = None
        self.delete_self = False
        self.delete_other = False