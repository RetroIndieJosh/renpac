from math import floor
from typing import Callable, Tuple

class Rect:
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0, 
                 on_pos_change: Callable[[int, int], bool] = None,
                 on_size_change: Callable[[int, int], bool] = None) -> None:
        """! Create a rectangle. In Ren'Py, (0, 0) is the top-left of the screen
        and increases going right and downwards.

        @param x The x coordinate of the rectangle's top-left corner.
        @param y The y coordinate of the rectangle's top-left corner.
        @param width The width of the rectangle.
        @param height The height of the rectangle.

        @param on_pos_change A function to be called when the rectangle's position
            changes. This must take four arugments (old_x, old_y, new_x, new_y)
            and return a boolean. The function is called before changing the
            Rect's position, and if it returns false, the change is aborted.

        @param on_size_change A function to be called when the rectangle's size
            changes. This must take four arugments (old_width, old_height,
            new_width, new_height) and return a boolean. The function is called
            before changing the Rect's size, and if it returns false, the change
            is aborted.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.on_pos_change = on_pos_change
        self.on_size_change = on_size_change

    def __repr__(self) -> str:
        """! Get a string representation of the rectangle (built-in)."""
        return str(self)

    def __str__(self) -> str:
        """! Get a string representation of the rectangle (built-in)."""
        left, top, right, bottom = self.get_ltrb()
        return f"[({left}, {top}) - ({right}, {bottom})] ({self.width} x {self.height})"

    @staticmethod
    def clone(rect: 'Rect') -> 'Rect':
        """! Create a copy of the given rectangle.

        @param rect The rectangle to copy.

        @return A new rectangle with its x, y, width, and height matching the given rectangle.
        """
        return Rect(*rect.get_xywh())

    def contains(self, x: int, y: int) -> bool:
        """! Determine whether the given point is within the given rectangle.

        @param x The x coordinate of the rectangle's top-left corner.
        @param y The y coordinate of the rectangle's top-left corner.

        @return True if the coordinate is in the rectangle, False otherwise.
        """
        left, top, right, bottom = self.get_ltrb()
        return x >= left and x <= right and y >= top and y <= bottom

    # TODO intersects(rect)

    def get_center(self) -> Tuple[int, int]:
        """! Get the center coordinate in the rectangle. In case of a
        non-integer center, the values are floored.

        @return A tuple with the values (x, y) of the center position, floored.
        """
        return self.x + floor(self.width * 0.5), self.y + floor(self.height * 0.5)

    def set_center(self, x, y) -> None:
        """! Position the rectangle such that the center is at the given
        coordinate. If the resulting rectangle position is a non-integer, the
        rectangle is shifted up and left to the nearest integer (values are
        floored). This triggers the on_pos_changed event.

        @param x The x coordinate of the new center position.
        @param y The y coordinate of the new center position.
        """
        self.set_pos(x - floor(self.width * 0.5), y - floor(self.height * 0.5))

    def get_ltrb(self) -> Tuple[int, int, int, int]:
        """! Get the left, top, right, and bottom for the rectangle.

        @return A tuple with values (left, top, right, bottom).
        """
        return self.x, self.y, self.x + self.width, self.y + self.height

    def set_ltrb(self, left: int, top: int, right: int, bottom: int) -> None:
        """! Set the rectangle position and size given a left, right, top, and
        bottom. This triggers both the on_pos_change and on_size_change events.

        @param left The leftmost point of the rectangle.
        @param top The topmost point of the rectangle.
        @param right The rightmost point of the rectangle.
        @param bottom The bottommost point of the rectangle.
        """
        self.set_pos(left, top)
        self.set_size(right - left, bottom - top)

    def get_size(self) -> Tuple[int, int]:
        """! Get the size of the rectangle.

        @return A tuple with values (width, height).
        """
        return self.width, self.height

    def set_size(self, width: int, height: int) -> None:
        """! Set the size of the rectangle and trigger on_size_change event.

        @param width The width of the rectangle.
        @param height The height of the rectangle.
        """
        if self.on_size_change is not None:
            if not self.on_size_change(self.width, self.height, width, height):
                return
        self.width = width
        self.height = height

    def get_pos(self) -> Tuple[int, int]:
        """! Get the position (top-left coordinate) of the rectangle.

        @return A tuple with values (x, y).
        """
        return self.x, self.y

    def set_pos(self, x, y) -> None:
        """! Set the position (top-left coordinate) of the rectangle.
        
        @param x The x position of the rectangle.
        @param y The y position of the rectangle.
        """
        if self.on_pos_change is not None:
            if not self.on_pos_change(self.x, self.y, x, y):
                return
        self.x = x
        self.y = y

    def get_xywh(self) -> Tuple[int, int, int, int]:
        """! Get the position and size of the rectangle.

        @return A tuple with values (x, y, width, height).
        """
        return self.x, self.y, self.width, self.height

    def set_xywh(self, x: int, y: int, width: int, height: int) -> None:
        """! Set the position and size of the rectangle.

        @param x The x coordinate of the rectangle's top-left corner.
        @param y The y coordinate of the rectangle's top-left corner.
        @param width The width of the rectangle.
        @param height The height of the rectangle.
        """
        self.set_pos(x, y)
        self.set_size(width, height)