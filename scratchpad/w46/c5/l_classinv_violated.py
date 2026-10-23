_ = 0  # anchor
class C:
    #@ class invariant self.n >= 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def bad(self) -> None:
        self.n = -1


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    c.bad()
    return 0
