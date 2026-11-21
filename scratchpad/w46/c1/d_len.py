_ = 0  # anchor
class C:
    def __init__(self) -> None:
        self.n: int = 0

    def __len__(self) -> int:
        return 3


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return len(c)
