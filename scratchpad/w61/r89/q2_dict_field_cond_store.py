from typing import Dict
class C:
    d: Dict[int, int]
    #@ assigns self.d
    def __init__(self, k: int) -> None:
        self.d = {1: 5}
        if k > 0:
            self.d = {1: 9}

#@ ensures \result == 5
def f() -> int:
    c = C(1)
    return c.d[1]
