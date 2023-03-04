from . import Action, Hotspot

class Exit(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.target = None
        self.width = 0
        self.height = 0

        self.action_left = Action.get("go")
        self.action_right = None
        self.action_middle = Action.get("examine")
        self.action_down = None
        self.action_up = None

    def go(self) -> None:
        if self.room is not None:
            Game.set_room(self.target) #type: ignore