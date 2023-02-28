from . import Hotspot

class Item(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.img_path = f"{self.name}_%s.png"

    def on_click(self) -> None:
        self.room.remove_hotspot(self)
        self.room = None
        global inventory_add
        inventory_add(self)