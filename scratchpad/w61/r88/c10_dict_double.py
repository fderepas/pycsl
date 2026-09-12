from typing import Dict
class C:
    d: Dict[int, int]
    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}
        self.d = {1: 9}

#@ ensures \result == 5
def f() -> int:
    c = C()
    return c.d[1]
