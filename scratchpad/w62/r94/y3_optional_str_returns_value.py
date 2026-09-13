from typing import Optional

def g() -> Optional[str]:
    return "a"

#@ ensures \result == 1
def f() -> int:
    r = g()
    if r is None:
        return 1
    return 0
