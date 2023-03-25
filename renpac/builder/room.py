from typing import Callable, Dict, List, Optional, Tuple

from renpac.builder import python
from renpac.builder.VariableMap import VariableMap, process_varmaps

room_varmaps = {
    "desc": VariableMap("desc"),
    "first": VariableMap("first_desc"),
    "printed": VariableMap("printed_name"),
}

def room_to_python(room_name: str, room_data: Dict[str, str]) -> List[str]:
    python_name = python.room(room_name)
    lines: List[str] = []
    lines.append(f"{python_name} = Room(\"{room_name}\")")
    lines += process_varmaps(python_name, room_varmaps, room_data)
    return lines