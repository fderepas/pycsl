K: int = 8


class C:
    x: int

    #@ assigns self.x
    def __init__(self) -> None:
        self.x = K + 1


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.x
