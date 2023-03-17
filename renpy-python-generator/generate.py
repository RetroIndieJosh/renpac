import argparse
import os

from GeneratorFile import GeneratorFile
from printv import *

parser = argparse.ArgumentParser()
 
parser.add_argument("-i", "--in", help = "Input Path: Path to *.py files to process")
parser.add_argument("-o", "--out", help = "Output Path: Path where *.gen.rpy files will be written")
parser.add_argument("-s", "--ignoresubdirs", action='store_true', help = "Ignore Subdirectories: Skip subdirectories (by default, flattens structure of input directory to find all *.py files)")
parser.add_argument("-v", "--verbose", action='store_true', help = "Verbose Mode: Show additional process messages")
 
args = vars(parser.parse_args())
 
input_path = args['in']
output_path = args['out']
if args['verbose']:
    enable_verbose()

FLATTEN = not args['ignoresubdirs']

if input_path is None or output_path is None:
    print("You must specify the input and output paths.")
    exit(0)

GeneratorFile.input_path = input_path
GeneratorFile.output_path = output_path

def cleanup():
    gen_files = list(filter(lambda file_name: 
        file_name.endswith(".gen.rpy"), os.listdir(output_path)))
    printv(f"cleaning up {len(gen_files)} files")
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

if FLATTEN:
    all_filenames = []
    for path, _, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(path, file)
            all_filenames.append(file_path[len(input_path)+1:])
else:
    all_filenames = os.listdir(input_path)
filenames = list(filter(file_valid, all_filenames))

if(len(filenames) == 0):
    print("no files!")
    exit()

printv(f"** loading files")
priority = 0
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