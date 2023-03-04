import logging

from . import Renpac

class Action:
    actions = {}
    current = None

    __create_key = object()

    @staticmethod
    def get(name) -> object:
        if name not in Action.actions:
            Renpac.warning(f"attempted to retrieve action '{name}' before it was registered")
        return Action.actions[name] if name in Action.actions else None

    @staticmethod
    def register(name, func) -> None:
        logging.info(f"register action '{name}'")
        Action.actions[name] = Action(Action.__create_key, name, func)

    def __init__(self, key, name, func) -> None:
        if key is not Action.__create_key:
            raise Exception("Use Action.register() to create a new action, not the Action() constructor.")
        self.name = name
        self.func = func
    
    def execute(self, target) -> None:
        logging.info(f"execute action '{self.name}' on '{target.name}'")
        self.func(target)
