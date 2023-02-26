class Hotspot:
    def __init__(self, name: str) -> None:
        self.name = name
        self.img_path = None

        self.x = 0
        self.y = 0
        self.width = 256
        self.height = 256

        self.room = None

    def on_click(self) -> None:
        raise NotImplementedError()

class Exit(Hotspot):
    def __init__(self, name: str, target_room: object, width: int, height: int) -> None:
        super().__init__(name)
        self.target_room = target_room
        self.width = width
        self.height = height

    def on_click(self) -> None:
        global set_room
        set_room(self.target_room)

class Item(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.img_path = f"{self.name}_%s.png"

    def on_click(self) -> None:
        self.room.remove_hotspot(self)
        self.room = None
        global inventory_add
        inventory_add(self)