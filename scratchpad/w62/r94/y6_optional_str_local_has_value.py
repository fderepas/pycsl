from typing import Optional

#@ ensures \result == 0
def f() -> int:
    r: Optional[str] = "a"
    if r is None:
        return 1
    return 0
