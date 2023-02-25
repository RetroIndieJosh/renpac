import os

ignore_list = [ "generate.py" ]
files = list(filter(lambda file_name: file_name.endswith(".py") and file_name not in ignore_list, os.listdir()))

if(len(files) == 0):
    print("no files!")
    exit()

print(f"generating {len(files)} files")
for py_file_name in files:
    with open(py_file_name) as file:
        file_data = file.read()
    print(f"{py_file_name}", end='')

    rpy_file_name = os.path.splitext(py_file_name)[0] + ".gen.rpy"

    with open(rpy_file_name, "w") as file:
        file.write("# THIS FILE WAS GENERATED BY RENPACS! DO NOT MODIFY MANUALLY AS CHANGES MAY BE OVERWRITTEN\n")
        file.write("# If you want to make changes, modify the relevant .py file and run the generator again.\n\n")
        file.write("init python:\n")
        for line in file_data.splitlines():
            file.write(f"    {line}\n")
    print(f" => {rpy_file_name}")

print("done")