_ = 0  # anchor
class C:
    k: int = 7

    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.k
