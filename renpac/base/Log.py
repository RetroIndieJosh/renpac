#priority -999
import logging

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from renpac.base.printv import enable_verbose, printv
from renpac.base.utility import text_menu

class Log:
    """! Wrap initialization and writing raw messages to the log. Most log
    access should use the Python built-in `logging` instead of this class.
    """

    _initialized: bool = False

    ## The default log level (not set, debug, info, warning, error, critical)
    _level: int = logging.NOTSET

    ## List of available log streams
    _log_list: List[str] = []

    ## Path to the log output file, or none to use standard output
    _path: Optional[Path] = None

    @staticmethod
    def init(title: Optional[str], path: Optional[Path] = None, log_level: int = logging.NOTSET):
        """! Initialize a log. 

        @param path The file path where the log will be stored.
        @param log_level The lowest level of messages to be displayed in the log.
        """
        ## Store the log path so we can write raw messages to it
        Log._path = None if path is None else path.absolute()

        Log._level = log_level

        # TODO can we avoid repetition here?
        if path is None:
            logging.basicConfig(
                format = '[%(asctime)s] %(levelname)s (%(levelno)s): %(message)s',
                encoding = 'utf-8', 
                level = log_level
            )
        else:
            logging.basicConfig(
                filename = Log._path,
                format = '[%(asctime)s] %(levelname)s (%(levelno)s): %(message)s',
                encoding = 'utf-8', 
                level = log_level
            )

        Log._initialized = True
        if title is not None:
            Log.write_header(f"{title}", timestamp=True)
        printv(f"Started log '{title}' at {Log._path}")

    @staticmethod
    def check_init():
        if not Log._initialized:
            raise Exception("Cannot use Log before init() is called")

    @staticmethod
    def clear():
        Log.check_init()
        with open(Log._path, 'w'):
            pass

    @staticmethod
    def delete():
        Log.check_init()
        Log._path.unlink()
        Log._initialized = False

    @staticmethod
    def get(log_name: str) -> logging.Logger:
        Log.check_init()
        if log_name not in Log._log_list:
            logging.error(f"Tried to get log named '{log_name}' but no such log registered")
        return logging.getLogger(log_name)

    @staticmethod
    def register(log_name: str, level: Optional[int] = None) -> None:
        Log.check_init()
        if log_name  in Log._log_list:
            return
        Log._log_list.append(log_name)
        if level is None:
            level = Log._level
        logging.getLogger(log_name).setLevel(level)

    @staticmethod
    def write_header(message: str, timestamp: bool = False) -> None:
        """! Write a distinguished header to the log.

        @param message The message to write to the file.
        @param timestamp If True, write a timestamp before the main header text.
        """
        Log.write(timestamp=False)
        Log.write_header_line()
        Log.write(message, timestamp)
        Log.write_header_line()
        Log.write(timestamp=False)

    @staticmethod
    def write_header_line():
        """! Write text to offset the header from normal log text. THis appears
        both before and after the main header text.
        """
        Log.check_init()
        Log.write(f"#####################################################################", timestamp=False)

    @staticmethod
    def write(message: str = "", newline: bool = True, timestamp: bool = True) -> None:
        """! Write a raw message to the log.

        @param message The message to write.
        @param newline If True, end the message with a newline.
        @param timestamp If True, begin the message with a timestamp in the
            format Year-Month-Day Hour:Minute:Second,Millisecond.
        """
        Log.check_init()
        if newline:
            message += '\n'
        if timestamp:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            message = f"[{now_str}] {message}"
        if Log._path is None:
            print(message)
        else:
            with open(Log._path, 'a') as log_file:
                log_file.write(message)

if __name__ == "__main__":
    enable_verbose()

    options = [
        ("write", "write a message to the log file"),
        ("clear", "clear the log file"),
        ("delete", "delete the log file"),
        ("quit", "delete the log file"),
    ]

    path = Path(__file__).parent.joinpath("test.log")
    Log.init("Test Log", path, logging.DEBUG)
    initialized = True

    choice: str = ""
    while choice != "quit":
        prompt = f"Select an option (log is {'' if initialized else 'not'} initialized)"
        choice = text_menu(prompt, options)
        if choice == "write":
            Log.write_header("This is a test header")
            Log.write("This is a test raw message")
            Log.write("This is a test raw message with no newline", False, False)
            Log.write("or timestamp", False, False)
        elif choice == "clear":
            Log.clear()
        elif choice == "delete":
            Log.delete()

    Log.clear()

    print("(tests incomplete)")