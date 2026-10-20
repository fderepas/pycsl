from typing import Any, Dict

#@ assigns \nothing
def any_truthy(rec: Dict[str, Any]) -> bool:
    if rec.get("answer"):
        return True
    return False
