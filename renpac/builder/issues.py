import logging
import os

from dataclasses import dataclass
from enum import Enum
from typing import List

from renpac.base.StaticClass import StaticClass

log = logging.getLogger("issues")

class Level(Enum):
    INFO = 0,
    WARNING = 1,
    ERROR = 2

@dataclass()
class Issue:
    message: str
    line: int
    level: Level

    def is_error(self) -> bool:
        return self.level == Level.ERROR

    def is_warning(self) -> bool:
        return self.level == Level.WARNING

    def print(self) -> None:
        color: str = ""
        if self.level == Level.WARNING:
            color = "\033[93m"
        elif self.level == Level.ERROR:
            color = "\033[91m"
        elif self.level == Level.INFO:
            color = "\033[96m"
        print(f"{color}[{self.level.name}]", end='')
        if self.line >= 0:
            print(f" Line {self.line}", end='')
        print(f": {self.message}")

class Manager(StaticClass):
    _issues: List[Issue] = []

    @staticmethod
    def add_error(error: str, line: int = -1):
        Manager.add_issue(error, line, Level.ERROR)
        log.error(error)

    @staticmethod
    def add_issue(message: str, line: int, level: Level):
        issue: Issue = Issue(message, line, level)
        Manager._issues.append(issue)

    @staticmethod
    def add_info(info: str, line: int = -1):
        Manager.add_issue(info, line, Level.INFO)
        log.warn(info)

    @staticmethod
    def add_warning(warning: str, line: int = -1):
        Manager.add_issue(warning, line, Level.WARNING)
        log.warn(warning)

    @staticmethod
    def count_errors() -> int:
        return sum(issue.is_error() for issue in Manager._issues)

    @staticmethod
    def count_warnings() -> int:
        return sum(issue.is_warning() for issue in Manager._issues)

    @staticmethod
    def has_error():
        return Manager.count_errors() > 0

    @staticmethod
    def has_warning():
        return Manager.count_warnings() > 0

    @staticmethod
    def print() -> None:
        os.system("color")
        print("************ BUILD MESSAGES ************")
        for issue in Manager._issues:
            issue.print()

        error_count = Manager.count_errors()
        warning_count = Manager.count_warnings()
        print(f"\033[0m{error_count} errors, {warning_count} warnings")
        print("************ END BUILD MESSAGES ************")
