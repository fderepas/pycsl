r"""constructor raising caught"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
