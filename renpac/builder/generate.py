import os

from typing import List, Optional

from renpac.base.printv import *

from renpac.builder.GeneratorFile import GeneratorFile
from renpac.builder.Path import Path

def cleanup(output_path: str) -> None:
    if not os.path.exists(output_path):
        return
    gen_files = list(filter(lambda file_name: 
        file_name.endswith(".gen.rpy"), os.listdir(output_path)))
    printv(f"cleaning up {len(gen_files)} .gen.rpy files from '{output_path}'")
    for gen_file_name in gen_files:
        os.remove(f"{output_path}/{gen_file_name}")

# TODO better name
# TODO pass in ignore list
# TODO option to decide whether ignore list should be exact (or contains)
def file_valid(filename: str) -> bool:
    # ignore any paths that *contain* the string 
    ignore_list = [ "__init__.py" ]
    if not filename.endswith(".py"):
        return False
    for ignore in ignore_list:
        if ignore in filename:
            return False
    return True

def get_filenames(input_path: str) -> List[str]:
    filenames = list(filter(file_valid, os.listdir(input_path))) 
    if(len(filenames) == 0):
        raise Exception(f"no files for generator in '{input_path}'")
    return filenames

# TODO split this up, it's massive!
def generate(input_path: str, output_path: str, input_subdirs:
    Optional[List[str]] = None) -> None:
    """! Convert python files from input_path to Ren'py files in output_path
        using dependency detection to calculate priority so Ren'py will load all
        Python scripts in the correct order.

    @param input_path The top-level input path containing all .py files.
    @param output_path The output path for all created .rpy files.
    @param input_subdirs If set, get all .py files from these subdirectories.
        This does not include the top-level input_path unless "." is one of the
        input_subdirs. If this is not set, only files from input_dir are
        included and any subdirectories are ignored.
    """
    if input_path is None or output_path is None:
        raise Exception("Generator requires both input and output paths.")

    input_path = Path(input_path).get()
    output_path = Path(output_path, check_exists=False).get()

    GeneratorFile.input_path = input_path
    GeneratorFile.output_path = output_path

    cleanup(output_path)

    filenames: List[str] = []
    if input_subdirs is None:
        filenames = get_filenames(input_path)
    else:
        subdir: str
        for subdir in input_subdirs:
            filenames += map(lambda filename: f"{subdir}/{filename}", get_filenames(Path(f"{input_path}/{subdir}").get()))

    if(len(filenames) == 0):
        print(f"no files for generator in '{input_path}'")
        exit(0)

    printv(f"** loading files")
    for py_file_name in filenames:
        f = GeneratorFile(py_file_name)
        GeneratorFile.files[str(f)] = f

    printv(f"** reading dependencies")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].extract_dependencies()

    printv(f"** linking dependencies")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].link_dependencies()

    printv(f"** setting priorities")
    root_files = []
    for key in GeneratorFile.files:
        if not GeneratorFile.files[key].is_dependency():
            root_files.append(GeneratorFile.files[key])
    file: GeneratorFile
    for file in root_files:
        printv(f"  -- root file: {file.name()}")
    for file in root_files:
        file.set_priority()

    printv(f"** checking manual priorities")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].check_priority()

    exit(0)

    printv(f"** generating {len(GeneratorFile.files)} files")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].write()

    print(f"{len(GeneratorFile.files)} files generated successfully")

if __name__ == "__main__":
    enable_verbose()
    generate("..", "../engine/rpy", ["base", "engine"])