class C:
    w: int

    #@ assigns self.w
    def __init__(self) -> None:
        self.w = 5


#@ requires True
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.w
