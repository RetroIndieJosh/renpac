import logging
from typing import Callable, Dict, Optional

from . import Renpac

class Action:
    """! An action the player can perform in the game targeting at most one
    hotspot. This is either called through context in the game or bound to a
    mouse button to trigger when a hotspot is clicked.
    """

    ## The list of registered actions.
    _actions: Dict[str, 'Action'] = {}

    ## Whether actions are locked, i.e. no more actions can be registered.
    _locked: bool = False

    ## The current active action.
    current: Optional['Action'] = None

    ## The default action for a given context.
    default: Optional['Action'] = None

    @staticmethod
    def get(name: str) -> Optional['Action']:
        """! Get an action by name. If it doesn't exist, throw a warning and
        return nothing.

        @return The Action of the given name, or None if it doesn't exist.
        """
        if name not in Action._actions:
            Renpac.warn(f"attempted to retrieve action '{name}' before it was registered")
            return None
        return Action._actions[name] if name in Action._actions else None

    @staticmethod
    def lock() -> None:
        """! Lock actions so no more can be regsitered. Actions should be
        registered early in the program run and then locked. Actions can be
        locked multiple times with no ill effect, but can never be unlocked.
        """
        Action._locked = True

    def __init__(self, name: Optional[str], func: Callable[['Hotspot'], None]) -> None: #type: ignore
        """! Create and register an action called \p name that executes function
        \p func. Throw an exception if actions are locked.

        @param name The name of the action, or None to register as \p #Action.default.
        
        @param func The function to call when executing the action. This must
        take one argument - the target hotspot - and return nothing.
        """
        if Action._locked:
            raise Exception(f"Attempted to create action, but actions are "
                "locked. Please create action '{name}' BEFORE locking.")

        self.name = name
        self.func = func

        self.allow_func: Callable[['Hotspot'], bool] = None #type: ignore
        self.disallowed_func: Callable[['Hotspot'], bool] = None #type: ignore

        if name is None:
            Action.default = self
        else:
            Action._actions[name] = self
    
    def execute(self, target: 'Hotspot') -> None: #type: ignore
        """! Execute the action on the given target.
        
        @param target The hotspot on which the #Action.func will execute.
        """
        if self.name is None:
            logging.info(f"execute default action on '{target.name}'")
        else:
            logging.info(f"execute action '{self.name}' on '{target.name}'")

        self.func(target)
