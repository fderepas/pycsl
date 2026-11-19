_ = 0  # anchor
class C:
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C()
    c.v = (1, 2)
    if c.v == 0:
        return 7
    return 0
