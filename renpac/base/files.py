import filecmp
import shutil
import os

from typing import Callable, Optional

# TODO should we have an exclude list as an arg, or pre-built exclude funcs?
# wasn't there a builtin for that?
def copy_tree(source_dir: str, dest_dir: str, 
        check_func: Optional[Callable[[str], bool]] = None, 
        relative_dir: str = "") -> int:
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
    dir = os.path.join(source_dir, relative_dir)
    count = 0
    for file in os.listdir(dir):
        source_file = os.path.join(source_dir, relative_dir, file)
        if os.path.isdir(source_file):
            count += copy_tree(source_dir, dest_dir, check_func,
                os.path.join(relative_dir, file))
        else:
            # TODO use logging.debug
            #printv(f"[{relative_dir}] ", end='')
            dest_file = os.path.join(dest_dir, relative_dir, file)
            if check_func is not None:
                if not check_func(dest_file):
                    continue
            # skip copy if the destination file matches exactly
            if os.path.exists(dest_file):
                if os.path.getsize(source_file) == os.path.getsize(dest_file):
                    if filecmp.cmp(source_file, dest_file, False):
                        # TODO use logging.debug
                        #printv(f"SKIP\n\t{source_file}")
                        continue
            # TODO use logging.debug
            #printv(f"COPY\n\t{source_file}\n\tTO {dest_file}")
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(source_file, dest_file)
            count += 1
    return count
