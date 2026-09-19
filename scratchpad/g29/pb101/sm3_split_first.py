from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s: str = "a,b"
    parts: List[str] = s.split(",")
    if parts[0] == "a,b":
        return 1
    return 0
