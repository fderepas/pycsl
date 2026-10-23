from typing import Dict
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    d: Dict[str, int] = {"k6404": 1, "k44509": 2}
    return d["k6404"]
