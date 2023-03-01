from . import Hotspot

class Exit(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.target = None
        self.width = 0
        self.height = 0

    # TODO handle as action
    def on_click(self) -> None:
        if self.room is not None:
            renpy.call("set_room", self.target) # type: ignore