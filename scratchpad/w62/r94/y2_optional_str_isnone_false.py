from typing import Optional

def g() -> Optional[str]:
    return None

#@ ensures \result == 0
def f() -> int:
    r = g()
    if r is None:
        return 1
    return 0
