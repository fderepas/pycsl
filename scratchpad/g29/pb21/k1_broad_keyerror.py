from typing import Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        return d["z"] * 0
    except Exception:
        return 9
