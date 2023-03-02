#priority -999
import logging

from os import getcwd
from datetime import datetime

class Log:
    _filename = ""

    @staticmethod
    def init(filename):
        Log._filename = filename

        logging.basicConfig(
            filename=filename,
            format='[%(asctime)s] %(levelname)s (%(levelno)s): %(message)s',
            encoding='utf-8', 
            level=logging.DEBUG
        )

        Log.write_header("RenPaC Log", timestamp=True)
        logging.info(f"Started log at {getcwd()}/{filename}")

    @staticmethod
    def write_header(message, timestamp=False):
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