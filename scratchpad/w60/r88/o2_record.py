from typing import Optional


class B:
    v: int

    #@ assigns self.v
    def __init__(self) -> None:
        self.v = 9


class C:
    b: Optional[B]

    #@ assigns self.b
    def __init__(self) -> None:
        self.b = B()


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    if c.b is None:
        return 1
    return 0
