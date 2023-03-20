import os
import platform

THIS_PATH: str = os.path.dirname(__file__)

# pathlib alone can probably do most of this, but feels like overkill
class Path:
    _platform = None

    def __init__(self, path: str, check_exists: bool = True) -> None:
        if Path._platform is None:
            Path._platform = platform.system()
        self._path: str = ""
        self.set(path)

        if check_exists and not os.path.exists(self._path):
            raise Exception(f"Cannot find path '{self._path}'")

    def __repr__(self) -> str:
        return self.get()

    def __str__(self) -> str:
        return self.get()

    def append(self, addend) -> None:
        self._path += addend
        self.normalize()

    def get(self) -> str:
        return self._path

    def is_absolute(self) -> bool:
        return self._path.startswith('/') or ':' in self._path

    def make_absolute(self) -> None:
        if self.is_absolute():
            return
        self._path = f"{THIS_PATH}/{self._path}"

    def normalize(self) -> None:
        if Path._platform == "Windows":
            self._path = self._path.replace('/', '\\')
        else:
            self._path = self._path.replace('\\', '/')

    def set(self, path) -> None:
        self._path = path
        self.make_absolute()
        self.normalize()