#from renpac.engine.Action import Action
#from renpac.engine.Hotspot import Hotspot
from . import Action, Hotspot

class Exit(Hotspot):
    """ A hotspot that leads to another room through "go" action
    """

    def __init__(self, name: str) -> None:
        """ Create an Exit

        @param name The unique name (handle) for the exit
        """
        super().__init__(name)

        ## The room we "go" to when this exit is activated
        self.target = None

        # init actions inherited from Hotspot
        self.action_left = Action.get("go")
        self.action_right = None
        self.action_middle = Action.get("examine")
        self.action_down = None
        self.action_up = None