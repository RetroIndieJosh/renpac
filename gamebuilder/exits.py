from VariableMap import *

exit_varmaps = [
]

def parse_exit(name: str) -> None:
    Script.add_line(f"# EXIT: {name}")

    config_key = f"exit.{name}"
    python_name = name.replace(' ', '_')
    Script.add_line(f"{python_name} = Exit(\"{name}\")")

    process_varmaps(exit_varmaps, config_key, python_name)