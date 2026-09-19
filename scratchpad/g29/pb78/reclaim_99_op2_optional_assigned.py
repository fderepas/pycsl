from typing import Optional
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    v: Optional[int] = None
    v = 5
    if v is None:
        return 1
    return 0
