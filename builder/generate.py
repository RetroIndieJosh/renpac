import argparse
import os

from GeneratorFile import GeneratorFile
from printv import *

def generate(input_path: str, output_path: str, flatten: bool = True) -> None:
    if input_path is None or output_path is None:
        print("You must specify the input and output paths.")
        exit(0)

    GeneratorFile.input_path = input_path
    GeneratorFile.output_path = output_path

    def cleanup():
        gen_files = list(filter(lambda file_name: 
            file_name.endswith(".gen.rpy"), os.listdir(output_path)))
        printv(f"cleaning up {len(gen_files)} .gen.rpy files from '{output_path}'")
        for gen_file_name in gen_files:
            os.remove(f"{output_path}/{gen_file_name}")

    cleanup()

    def file_valid(filename: str) -> bool:
        # ignore any paths that *contain* the string 
        ignore_list = [ "__init__.py" ]
        if not filename.endswith(".py"):
            return False
        for ignore in ignore_list:
            if ignore in filename:
                return False
        return True

    if flatten:
        all_filenames = []
        for path, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(path, file)
                all_filenames.append(file_path[len(input_path)+1:])
    else:
        all_filenames = os.listdir(input_path)
    filenames = list(filter(file_valid, all_filenames))

    if(len(filenames) == 0):
        print(f"no files for generator in '{input_path}")
        exit(0)

    printv(f"** loading files")
    for py_file_name in filenames:
        name = os.path.splitext(py_file_name)[0]
        GeneratorFile.files[name] = GeneratorFile(name)

    printv(f"** reading dependencies")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].find_dependencies()

    printv(f"** linking dependencies")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].link_dependencies()

    printv(f"** setting priorities")
    root_files = []
    for key in GeneratorFile.files:
        if not GeneratorFile.files[key].is_dependency:
            root_files.append(GeneratorFile.files[key])
    for file in root_files:
        printv(f"  -- root file: {file.name}")
    for file in root_files:
        file.set_priority()

    printv(f"** checking manual priorities")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].check_priority()

    printv(f"** generating {len(GeneratorFile.files)} files")
    for key in GeneratorFile.files:
        GeneratorFile.files[key].write()

    print(f"{len(GeneratorFile.files)} files generated successfully")