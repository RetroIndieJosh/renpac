import os

print("building...")

ignore_list = [ "generate.py" ]
files = list(filter(lambda file_name: file_name.endswith(".py") and file_name not in ignore_list, os.listdir()))

if(len(files) == 0):
    print("no files!")
    exit()

print(f"processing {len(files)} files")
for py_file_name in files:
    with open(py_file_name) as file:
        file_data = file.read()
    print(f"read ${py_file_name}")

    rpy_file_name = os.path.splitext(py_file_name)[0] + ".gen.rpy"
    print(f"outputting to ${rpy_file_name}")

    line_count = 0
    with open(rpy_file_name, "w") as file:
        file.write("init python:\n")
        for line in file_data.splitlines():
            file.write(f"    {line}\n")
            line_count += 1
    print(f"wrote {line_count} lines")

print("done")