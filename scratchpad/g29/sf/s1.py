r"""self field list read after method appends via self"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = []

    #@ assigns self.xs
    def add(self, v: int) -> None:
        self.xs.append(v)


#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.add(3)
    return len(c.xs)


if __name__ == "__main__":
    print("CPython:", probe())
