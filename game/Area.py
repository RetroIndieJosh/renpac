class Area:
    def __init__(self, other=None):
        if other is None:
            self.x = 0
            self.y = 0
            self.width = 0
            self.height = 0
        else:
            self.x = other.x
            self.y = other.y
            self.width = other.width
            self.height = other.height
