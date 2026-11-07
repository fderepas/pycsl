from typing import List
_ = 0  # anchor


#@ class invariant \length(self.xs) == 2
class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]

    #@ assigns self.xs
    def shrink(self) -> int:
        self.xs = [1]
        return 0


#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.shrink()
    return len(c.xs)
