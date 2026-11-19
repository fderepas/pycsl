from typing import Dict
class C:
    d: Dict[int, int]
    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}
        self.d = {1: 9, 2: 8}

#@ ensures \result == 1
def f() -> int:
    c = C()
    return len(c.d)
