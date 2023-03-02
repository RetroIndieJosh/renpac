import logging

from os import getcwd
from datetime import datetime

class Log:
    @staticmethod
    def init():
        logging.basicConfig(
            filename='renpac.log', 
            format='[%(asctime)s] %(levelname)s (%(levelno)s): %(message)s',
            encoding='utf-8', 
            level=logging.DEBUG
        )

        filename = 'renpac.log'
        with open(filename, 'a') as log_file:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n#####################################################################\n")
            log_file.write(f"RenPaC Log ({now_str})\n")
            log_file.write(f"#####################################################################\n\n")
        
        logging.info(f"Started log at {getcwd()}/{filename}")