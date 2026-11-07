from typing import Optional

#@ ensures \result == 1
def f() -> int:
    r: Optional[str] = None
    if r is None:
        return 1
    return 0
