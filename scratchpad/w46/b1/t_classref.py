_ = 0  # anchor
class C:
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = C
    if x:
        return 7
    return 0
