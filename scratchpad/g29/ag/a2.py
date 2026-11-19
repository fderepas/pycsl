r"""augmented assign on field"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1


#@ ensures \result == 1
def probe() -> int:
    c = C()
    c.n += 2
    return c.n


if __name__ == "__main__":
    print("CPython:", probe())
