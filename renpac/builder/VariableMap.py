import logging

from typing import Dict, List

from renpac.base.Config import ConfigEntry, ConfigType

from renpac.builder.RenpyScript import *

log = logging.getLogger("VariableMap")

class VariableMap(ConfigEntry):
    def __init__(self, python_key: str,
            expected_type: ConfigType = ConfigType.STRING, 
            is_required: bool = False, fallback: Optional[str] = None) -> None:
        self.python_key: str = python_key
        super().__init__(expected_type, is_required, fallback)

def process_varmaps(python_name: str, varmaps: Dict[str, VariableMap], data: Dict[str, str]) -> List[str]:
    lines: List[str] = []
    key: str
    for key in [key for key in varmaps if key in data]:
        lines.append(f"{python_name}.{key} = {varmaps[key].python_key}")
    print(lines)
    return lines