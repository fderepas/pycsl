from typing import Any


class C:
    def __init__(self):
        self.a: int = 7


#@ requires True
#@ ensures \result == 1
def peek(o: Any) -> int:
    v = getattr(o, "a", 0)
    if v == 0:
        return 1
    return 2
