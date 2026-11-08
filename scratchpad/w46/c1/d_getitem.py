_ = 0  # anchor
class C:
    def __init__(self) -> None:
        self.n: int = 0

    def __getitem__(self, i: int) -> int:
        return 7


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c[0]
