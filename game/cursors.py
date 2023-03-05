import os

cursor_dir_path = f"game/gui/cursors"
print(cursor_dir_path)
cursor_filenames = list(filter(lambda file_name: file_name.endswith(".png"), os.listdir(cursor_dir_path)))
print(f"cursor filenames: {cursor_filenames}")
for cursor_filename in cursor_filenames:
    print(f"process cursor {cursor_filename}")
    name = os.path.splitext(cursor_filename)[0]
    print(f"name is {name}")
    print(f"[ ( 'gui/cursors/{cursor_filename}', 0, 0)]")
    #config.mouse[name] = [ ( "gui/cursors/[cursor_filename]", 0, 0)]
    #print(f"config added: {config.mouse[name]}")