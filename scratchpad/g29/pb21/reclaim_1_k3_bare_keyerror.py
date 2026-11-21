from typing import Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        return d["z"] * 0
    except:
        return 9
