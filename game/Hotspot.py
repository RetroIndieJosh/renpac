class Hotspot:
    def __init__(self, name: str) -> None:
        # TODO name must be unique since we're using it as key, probably best to
        # have all hotspots use unique names so these can identify them
        # (would it be better to store in a game dict instead of name being part of hotspot?)
        self.name = name
        self.img_path = None

        self.x = 0
        self.y = 0
        self.width = 256
        self.height = 256

        # a mapping of item names to funcs to trigger when item is used on this hotspot
        self.on_use = dict()

        self.room = None

    def add_usable(self, item, func):
        self.on_use[item.name] = func

    def on_click(self) -> None:
        raise NotImplementedError()

    # combine item with this hotspot
    # returns True if the combination succeeded
    def combine(self, item) -> bool:
        if(item.name not in self.on_use):
            return False

        self.on_use[item.name]()
        return True

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