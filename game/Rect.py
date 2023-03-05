class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.pos_change = None
        self.size_change = None

    @staticmethod
    def clone(rect: 'Rect') -> 'Rect':
        return Rect(*rect.get_xywh())

    def get_ltrb(self) -> tuple:
        """! Return a tuple with values for (left, right, top, bottom).
        """
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def set_ltrb(self, left, right, top, bottom):
        self.set_pos(left, top)
        self.set_size(right - left, bottom - top)

    def get_size(self) -> tuple:
        """! Get the size of the rectangle (width, height)."""
        return (self.width, self.height)

    def set_size(self, width, height) -> None:
        self.width = width
        self.height = height
        if self.size_change is not None:
            self.size_change()

    def get_pos(self) -> tuple:
        """! Get the position (top-left coordinate) of the rectangle."""
        return (self.x, self.y)

    def set_pos(self, x, y) -> None:
        self.x = x
        self.y = y
        if self.pos_change is not None:
            self.pos_change()

    def get_xywh(self) -> tuple:
        return (self.x, self.y, self.width, self.height)

    def set_xywh(self, x, y, width, height) -> None:
        self.set_pos(x, y)
        self.set_size(width, height)