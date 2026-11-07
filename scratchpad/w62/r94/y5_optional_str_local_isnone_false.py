from typing import Optional

#@ ensures \result == 0
def f() -> int:
    r: Optional[str] = None
    if r is None:
        return 1
    return 0
