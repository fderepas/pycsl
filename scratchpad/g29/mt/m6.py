r"""match class pattern with isinstance"""
from typing import List, Tuple
_ = 0  # anchor


class P:
    def __init__(self, v: int) -> None:
        self.v = v


class Q:
    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result == 1
def probe() -> int:
    o = Q(3)
    match o:
        case P():
            return 1
        case _:
            return 2


if __name__ == "__main__":
    print("CPython:", probe())
