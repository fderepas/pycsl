_ = 0  # anchor
class C:
    def __init__(self) -> None:
        self.n: int = 0

    def __eq__(self, other: int) -> int:
        return 0


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    a = C()
    b = C()
    if a == b:
        return 7
    return 0
