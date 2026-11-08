from typing import Any

_ = 0  # anchor


#@ ensures \result == 0
def f(o: Any, p: Any) -> int:
    d = getattr(o, "a", {})
    e = getattr(p, "b", {})
    if d == e:
        return 0
    return 1
