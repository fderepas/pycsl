r"""subclass super init raising caught"""
from typing import List, ClassVar
_ = 0  # anchor


class B:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


class D(B):
    def __init__(self, v: int) -> None:
        super().__init__(v)
        self.w = 1


#@ ensures \result == 0
def probe() -> int:
    try:
        d = D(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
