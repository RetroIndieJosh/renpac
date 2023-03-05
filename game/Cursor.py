from . import Renpac

class Cursor:
    @staticmethod
    def reset() -> None:
        global default_mouse
        default_mouse = "default"

    @staticmethod
    def set(cursor_name: str) -> None:
        global config
        if cursor_name not in config.mouse:
            Renpac.warn(f"no mouse cursor '{cursor_name}' in config")

        global default_mouse
        default_mouse = cursor_name
