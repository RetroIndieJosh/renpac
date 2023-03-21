from renpac.engine.Renpac import Renpac

class Cursor:
    """! Helper class to set the Ren'py cursor image
    """

    @staticmethod
    def reset() -> None:
        """! Reset to the default cursor
        """
        global default_mouse
        default_mouse = "default" #type: ignore

    @staticmethod
    def set(cursor_name: str) -> None:
        """! Set the cursor image

        @param cursor_name The name of the cursor defined in options.rpy to replace the current cursor
        """
        global config
        if cursor_name not in config.mouse: #type: ignore
            Renpac.warn(f"no mouse cursor '{cursor_name}' in config")

        global default_mouse
        default_mouse = cursor_name #type: ignore
