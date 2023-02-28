from . import Hotspot

class Action:
    def __init__(self, name: str, func: function) -> None:
        self.name = name
        self.func = func
    
    def execute(self, target: Hotspot) -> None:
        self.func(target)
