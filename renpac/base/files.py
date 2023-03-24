import filecmp
import logging
import shutil
import os

from pathlib import Path
from typing import Callable, List, Optional

from renpac.base.printv import printv
from renpac.base.utility import indent

log = logging.getLogger("files")

def clear_dir(dir_path: Path, extensions: Optional[List[str]] = None) -> None:
    if not dir_path.exists():
        log.debug(f"Skip clearing dir '{dir_path}' - does not exist")
        return
    log.info(f"Delete all {extensions} in {dir_path}")
    for file_name in os.listdir(dir_path):
        if extensions is None or is_type(file_name, extensions):
            path = dir_path.joinpath(file_name)
            log.debug(f"DELETE '{path}'")
            os.remove(path)

# TODO change to Path (not str)
# TODO should we have an exclude list as an arg, or pre-built exclude funcs?
# wasn't there a builtin for that?
def copy_tree(source_dir: str, dest_dir: str, 
        check_func: Optional[Callable[[str], bool]] = None, 
        relative_dir: str = "", depth: int = 0) -> int:
    """! Recursively copy all files from the source directory to the target
    directory, including all subdirectories.

    @param source_dir The top-level directory containing files and
        directories to copy
    @param dest_dir The top-level destintation directory
    @param check_func A function to check whether a given file is valid
    @param relative_dir The directory relative to source_dir we are
        currently copying (used for recursion)
    @return The total number of files (excluding directories) copied
    """
    for line in indent(f"COPY DIR\n{source_dir}\n => {dest_dir}", depth, True).splitlines():
        log.debug(line)
    dir = os.path.join(source_dir, relative_dir)
    count = 0
    for file in os.listdir(dir):
        source_file = os.path.join(source_dir, relative_dir, file)
        if os.path.isdir(source_file):
            count += copy_tree(source_dir, dest_dir, check_func,
                os.path.join(relative_dir, file), depth + 1)
        else:
            dest_file = os.path.join(dest_dir, relative_dir, file)
            if check_func is not None:
                if not check_func(dest_file):
                    continue
            # skip copy if the destination file matches exactly
            if os.path.exists(dest_file):
                if os.path.getsize(source_file) == os.path.getsize(dest_file):
                    if filecmp.cmp(source_file, dest_file, False):
                        for line in indent(f"SKIP\n\t{source_file}", depth, True).splitlines():
                            log.debug(line)
                        continue
            for line in indent(f"COPY\n{source_file}\n => {dest_file}", depth, True).splitlines():
                log.debug(line)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(source_file, dest_file)
            count += 1
    return count

# TODO move somewhere even more basic than files since we can use this for anything (error.py?)
def exist_message(name: Path, exists: bool):
    return f"'{name}' does {'' if exists else 'not'} exist"

def filter_files(files: List[str], extensions: List[str], ignore: List[str] = []):
    filtered = []
    for file in filter(lambda file: file not in ignore, files):
        if is_type(file, extensions):
            filtered.append(file)
    return filtered

def is_type(file_name: str, extensions: List[str]) -> bool:
    for extension in filter(lambda ext: not ext.startswith('.'), extensions):
        raise Exception(f"Illegal file type '{extension}'. Must begin with a period.")
    return len(list(filter(lambda ext: file_name.endswith(ext), extensions))) > 0

def validate_path(path: Path) -> None:
    if not path.exists():
        raise Exception(f"Required path '{path}' cannot be read or does not exist")