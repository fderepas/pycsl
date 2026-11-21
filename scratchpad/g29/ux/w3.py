r"""dunder add raising caught"""
from typing import List, Dict
_ = 0  # anchor


class V:
    def __init__(self, x: int) -> None:
        self.x = x

    def __add__(self, o: "V") -> "V":
        raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        v = V(1) + V(2)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
