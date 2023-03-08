from VariableMap import *

combo_varmaps = [
]

def parse_combo(name: str) -> None:
    Script.add_line(f"# COMBO: {name}")

    config_key = f"combo.{name}"
    python_name = name.replace(' ', '_')
    Script.add_line(f"{python_name} = Combination(\"{name}\")")
    process_varmaps(combo_varmaps, config_key, python_name)

