from typing import List
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "a,b,c"
    parts: List[str] = s.split(",")
    return len(parts) - 2
