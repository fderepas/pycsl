class C:
    x: int

    #@ assigns self.x
    def __init__(self, n: int) -> None:
        self.x = n + 1


#@ requires True
#@ ensures \result == 6
#@ assigns \nothing
def f() -> int:
    c = C(5)
    return c.x
