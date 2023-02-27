class Combination:
    def __init__(self) -> None:
        self.func = None
        self.delete_self = False
        self.delete_target = False

class Hotspot:
    def __init__(self, name: str) -> None:
        # TODO name must be unique since we're using it as key, probably best to
        # have all hotspots use unique names so these can identify them
        # (would it be better to store in a game dict instead of name being part of hotspot?)
        # (or use a unique ID that increments instead? it's silly to have name
        # clashes, but what if there's something in multiplicity like coins?)

        self.name = name
        self.desc = name
        self.img_path = None

        self.x = 0
        self.y = 0
        self.width = 256
        self.height = 256

        # a mapping of item names to funcs to trigger when item is used on this hotspot
        self.combinations = dict()

        self.room = None

    def add_combination(self, item: object, combination: Combination):
        if item.name in self.combinations:
            raise Exception(f"{item.name} is already a key in combinations for {self.name}!")
        self.combinations[item.name] = combination

    def on_click(self) -> None:
        raise NotImplementedError()

    # combine item with this hotspot
    def combine(self, item: object) -> Combination:
        return self.combinations[item.name] if item.name in self.combinations else None

class Exit(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.target = None
        self.width = 0
        self.height = 0

    def on_click(self) -> None:
        if self.room is not None:
            set_room(self.target) # type: ignore

class Item(Hotspot):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.img_path = f"{self.name}_%s.png"

    def on_click(self) -> None:
        self.room.remove_hotspot(self)
        self.room = None
        global inventory_add
        inventory_add(self)