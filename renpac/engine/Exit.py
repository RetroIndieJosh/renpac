from typing import Optional

from renpac.engine.Action import Action
from renpac.engine.Hotspot import Hotspot
from renpac.engine.Room import Room

class Exit(Hotspot):
    """ A hotspot that leads to another room through "go" action
    """

    def __init__(self, name: str, has_image: bool = False) -> None:
        """ Create an Exit

        @param name The unique name (handle) for the exit
        """
        super().__init__(name)

        ## The room we "go" to when this exit is activated
        self.target: Optional[Room] = None

        # init actions inherited from Hotspot
        self.action_left: Action = Action.get("go")

        self._has_image: bool = has_image

    def get_img_path(self) -> Optional[str]:
        if self._has_image:
            return f"{self.name}.png"
        return None