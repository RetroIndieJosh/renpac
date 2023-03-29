import logging

from dataclasses import dataclass
from typing import Dict, List, Optional

from renpac.base import Config

from renpac.builder.RenpyScript import ScriptObject

log = logging.getLogger("VariableMap")

@dataclass(frozen = True)
class VarMap:
    renpac_key: str
    python_key: Optional[str] = None
    expected_type: Config.Type = Config.Type.STRING
    required: bool = False

def map_varmaps(obj: ScriptObject, varmaps: List[VarMap], data: Dict[str, str]):
    for varmap in [varmap for varmap in varmaps if varmap.renpac_key in data]:
        python_key: str = varmap.renpac_key if varmap.python_key is None else varmap.renpac_key
        obj.add_value(python_key, data[varmap.renpac_key], varmap.expected_type)
