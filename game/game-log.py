# TODO create a custom logger to use an external config
# see https://docs.python.org/3/howto/logging.html
import os
print(f"Logging in {os.getcwd()}")

import logging
from datetime import datetime
logging.basicConfig(
    filename='renpac.log', 
    format='[%(asctime)s] %(levelname)s (%(levelno)s): %(message)s',
    encoding='utf-8', 
    level=logging.DEBUG
)

with open('renpac.log', 'a') as log_file:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"#####################################################################\n")
    log_file.write(f"RenPaC Log ({now_str})\n")
    log_file.write(f"#####################################################################\n")
