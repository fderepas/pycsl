from typing import Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    d: Dict[str, int] = {}
    d["k6404"] = 1
    d["k44509"] = 2
    return d["k6404"]
