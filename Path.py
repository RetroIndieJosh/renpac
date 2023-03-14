import os
import platform

THIS_PATH = os.path.dirname(__file__)

# python probably has something like this, but pathlib is overkill
class Path:
    _platform = None

    def __init__(self, path, check_exists=True) -> None:
        if Path._platform is None:
            Path._platform = platform.system()
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