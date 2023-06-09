import logging

from dataclasses import dataclass
from typing import Dict, List, Optional

from renpac.base import Config
from renpac.builder import python

log = logging.getLogger("VariableMap")

@dataclass(frozen = True)
class VariableMap:
    renpac_key: str
    python_key: Optional[str] = None
    expected_type: Config.Type = Config.Type.STRING
    required: bool = False

def map_varmaps(obj: python.Object, varmaps: List[VariableMap], data: Dict[str, str]):
    for varmap in [varmap for varmap in varmaps if varmap.renpac_key in data]:
        python_key: str = varmap.renpac_key if varmap.python_key is None else varmap.python_key
        obj.add_value(python_key, data[varmap.renpac_key], varmap.expected_type)
