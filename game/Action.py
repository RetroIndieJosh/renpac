import logging

from . import Renpac

class Action:
    __create_key = object()

    _actions = {}

    current = None
    default = None

    @staticmethod
    def get(name) -> object:
        if name not in Action._actions:
            Renpac.warn(f"attempted to retrieve action '{name}' before it was registered")
        return Action._actions[name] if name in Action._actions else None

    @staticmethod
    def register(name, func) -> None:
        logging.info(f"register action '{name}'")
        action = Action(Action.__create_key, name, func)
        if name is None:
            Action.default = action
        else:
            Action._actions[name] = action

    def __init__(self, key, name, func) -> None:
        if key is not Action.__create_key:
            raise Exception("Use Action.register() to create a new action, not the Action() constructor.")
        self.name = name
        self.func = func
    
    def execute(self, target) -> None:
        if self.name is None:
            logging.info(f"execute default action on '{target.name}'")
        else:
            logging.info(f"execute action '{self.name}' on '{target.name}'")
        self.func(target)
