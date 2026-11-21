_ = 0  # anchor
class C:
    xs: list = []

    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = C()
    b = C()
    a.xs.append(1)
    return len(b.xs)
