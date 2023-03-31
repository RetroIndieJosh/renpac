# TODO put all print statements back to log.debug once tests work
import filecmp
import logging
import shutil

from pathlib import Path
from typing import Callable, List, Optional

from renpac.base.printv import printv
from renpac.base.utility import indent

log = logging.getLogger("files")

def clear_dir(dir_path: Path, extensions: Optional[List[str]] = None, 
        recursive: bool = True) -> None:
    """! Clear a directory of all files matching the given extensions, or of all
        files if no extensions are specified. Note this removes *only* files and
        does *not* remove *any* directories, even in recursive mode.

        @param dir_path Path of the root directory
        @param extensions List of string extensions to remove. These must begin
            with a period, i.e. [".txt", ".exe"]. If None, all files will be
            removed.
        @param recursive Whether to scan directories recursively. The same
            extension filter will be used, and no directories will be removed.
    """
    if not dir_path.exists():
        print(f"skip clearing dir '{dir_path}' - does not exist")
        return
    print(f"delete all {extensions} in {dir_path}")
    for file_path in dir_path.iterdir():
        if recursive and file_path.is_dir():
            clear_dir(file_path, extensions)
            continue
        if extensions is None or is_type(file_path, extensions):
            path = dir_path.joinpath(file_path)
            print(f"DELETE '{path}'")
            file_path.unlink()

# TODO change to Path (not str)
# TODO should we have an exclude list as an arg, or pre-built exclude funcs?
# wasn't there a builtin for that?
def copy_tree(source_root_dir: Path, dest_root_dir: Path, 
        check_func: Optional[Callable[[Path], bool]] = None, 
        # TODO somehow relative_dir needs to stay RELATIVE
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
    source_dir: Path = source_root_dir.joinpath(relative_dir).resolve()
    print(f"source_dir = {source_dir}")
    for line in indent(f"COPY DIR\n{source_dir}\n => {dest_root_dir}", depth, True).splitlines():
        print(line)
    dest_dir: Path = dest_root_dir.joinpath(relative_dir)
    if source_dir in dest_dir.parents:
        raise Exception("Cannot copy a directory tree inside itself as it will cause infinite recursion")
    dest_dir.mkdir(exist_ok=True)

    file_count: int = 0
    for file_path in source_dir.iterdir():
        source_path: Path = source_dir.joinpath(file_path)
        if source_path.is_dir():
            next_dir: str = relative_dir
            if next_dir != "":
                next_dir += "/"
            next_dir += file_path.name
            file_count += copy_tree(source_root_dir, dest_root_dir, check_func,
                next_dir, depth + 1)
            continue
        dest_file: Path = dest_dir.joinpath(file_path.name)
        if check_func is not None:
            if not check_func(dest_file):
                continue
        # skip copy if the destination file matches exactly
        if dest_file.exists() and source_path.stat().st_size == dest_file.stat().st_size \
                and filecmp.cmp(source_path, dest_file, False):
            for line in indent(f"SKIP IDENTICAL\n\t{source_path}\n == {dest_file}", depth, True).splitlines():
                print(line)
            continue
        for line in indent(f"COPY\n{source_path}\n => {dest_file}", depth, True).splitlines():
            print(line)
        shutil.copy2(source_path, dest_file)
        file_count += 1
    return file_count

# TODO move to text.py
def exist_message(name: Path, exists: bool) -> str:
    return f"'{name}' does {'' if exists else 'not'} exist"

# TODO use pattern matching for ignore
def filter_files(files: List[Path], extensions: List[str], ignore: List[str] = []):
    """! Filter  a list of files by extension, ignoring any files in the ignore list.

    @param files The list of files to filter as pathlib Paths
    @param extensions The list of extensions to include. These must begin with a
        period, i.e. [".txt", ".exe"].
    @param ignore THe list of files to ignore. These will only ignore if they
        match exactly the full file name (no pattern matching).
    @return A list of Pathlib paths matching the given filter (no path
        validation)
    """
    filtered = []
    for file in [file for file in files if str(file) not in ignore]:
        if is_type(file, extensions):
            filtered.append(file)
    return filtered

def is_type(file_name: Path, extensions: List[str]) -> bool:
    for extension in filter(lambda ext: not ext.startswith('.'), extensions):
        raise Exception(f"Illegal file type '{extension}'. Must begin with a period.")
    return len(list(filter(lambda ext: str(file_name).endswith(ext), extensions))) > 0

def validate_path(path: Path) -> bool:
    if not path.exists():
        raise Exception(f"Required path '{path}' cannot be read or does not exist")
    return True

## TESTS

TEST_FILE_PATH = Path(__file__)
TEMP_DIR_NAME = "temp"

# TODO call this on test init
def create_temp_tree() -> Path:
    temp_path: Path = Path(TEST_FILE_PATH.parent.joinpath(TEMP_DIR_NAME))
    temp_path.mkdir()
    for i in range(3):
        dir_path: Path = temp_path.joinpath(f"dir_{i}")
        dir_path.mkdir()
        for k in range(3):
            file_path: Path = dir_path.joinpath(f"file_{k}.txt")
            file_path.write_text("This is a test file for renpac.base.files and should not exist!")
    return temp_path.resolve()

# TODO call this on test cleanup
def delete_temp_tree() -> None:
    shutil.rmtree(TEMP_DIR_NAME)

def test_clear_dir() -> None:
    temp_path: Path = create_temp_tree()
    try:
        clear_dir(temp_path)
        assert len([path for path in temp_path.iterdir() if not path.is_dir()]) == 0
    finally:
        delete_temp_tree()

def test_copy_tree() -> None:
    temp_path: Path = create_temp_tree()
    copied_path: Path = TEST_FILE_PATH.parent.joinpath("temp-copy")
    try:
        # check that the right number of files (not including directories) were copied
        assert copy_tree(temp_path, copied_path) == len([path for path in temp_path.glob("**/*") if not path.is_dir()])

        # check we have the right number of files+directories
        temp_names = [path.name for path in temp_path.glob("**/*")]
        copied_names = [path.name for path in copied_path.glob("**/*")]
        assert len(temp_names) == len(copied_names)

        # check all file/directory names match
        for name in temp_names:
            assert name in copied_names
        
        # if we repeat the copy, we should copy no files (they are all identical)
        assert copy_tree(temp_path, copied_path) == 0

        # we cannot copy a tree into a subdirectory of the tree
        try:
            copy_tree(temp_path, temp_path.joinpath("subdir"))
        except:
            assert True
        else:
            assert False
        
    finally:
        delete_temp_tree()
        shutil.rmtree(copied_path)

def test_filter_files():
    files = [
        Path("this.txt"),
        Path("is.txt"),
        Path("a.exe"),
        Path("test.exe"),
        Path("and.exe"),
        Path("none.py"),
        Path("of.py"),
        Path("these.py"),
        Path("files.py"),
        Path("need.foo"),
        Path("exist"),
    ]
    assert len(filter_files(files, [".txt"])) == 2
    assert len(filter_files(files, [".exe"])) == 3
    assert len(filter_files(files, [".py"])) == 4
    assert len(filter_files(files, [".txt", ".exe", ".py"])) == 9
    assert len(filter_files(files, [".txt", ".exe", ".py"], ["a.exe", "and.exe"])) == 7
    assert len(filter_files(files, [".txt"], ["is.txt"])) == 1

def test_is_type():
    assert is_type(TEST_FILE_PATH, ['.py'])
    assert not is_type(TEST_FILE_PATH, ['.exe', '.bat', '.txt', '.rpy', '.pyc'])
    assert validate_path(Path(__file__)) == True

def test_validate_path():
    assert validate_path(Path(__file__)) == True