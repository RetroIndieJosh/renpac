#priority -999
import logging

from os import getcwd
from datetime import datetime

class Log:
    ## the log filename, stored so we can write raw messages to it
    _filename = ""

    @staticmethod
    def init(filename):
        """! Initialize the log. Only one log can be initialized at a time. Any
        calls to `logging` methods will refer to this log.

        @param filename The filename where the log will be stored. For now, this
        is in the Ren'py executable directory. Initializing the log will print
        the full path to the log to the terminal.
        """
        Log._filename = filename

        logging.basicConfig(
            filename=filename,
            format='[%(asctime)s] %(levelname)s (%(levelno)s): %(message)s',
            encoding='utf-8', 
            level=logging.DEBUG
        )

        Log.write_header("RenPaC Log", timestamp=True)
        print(f"Started log at {getcwd()}/{filename}")

    @staticmethod
    def write_header(message, timestamp=False):
        """! Write a header to the log. This will be distinguished with a line
        of hashes and a blank line before and after the header.

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
        Log.write(f"#####################################################################", timestamp=False)

    @staticmethod
    def write(message="", newline=True, timestamp=True) -> None:
        with open(Log._filename, 'a') as log_file:
            if newline:
                message = f"{message}\n"
            if timestamp:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
                message = f"[{now_str}] {message}"
            log_file.write(message)

Log.init('renpac.log')