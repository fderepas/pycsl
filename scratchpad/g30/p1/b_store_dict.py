from typing import Dict, Optional


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, Optional[int]] = {"a": 1}
    d["a"] = None
    v = d["a"]
    if v == 0:
        return 1
    return 2
