from typing import Any, Dict
PyVal = Any

#@ assigns \nothing
def has_key(rec: Dict[str, PyVal]) -> bool:
    inner = rec.get("term") or {}
    if "loc" in inner:
        return True
    return False
