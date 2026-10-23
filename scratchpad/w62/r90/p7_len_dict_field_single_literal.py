from typing import Dict
class C:
    d: Dict[int, int]
    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5, 2: 6}

#@ ensures \result == 0
def f() -> int:
    c = C()
    return len(c.d)
