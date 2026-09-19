from typing import Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    v: Optional[int] = None
    if v is None:
        return 1
    return 0
