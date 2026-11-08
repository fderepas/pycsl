r"""raising init called from helper under no_exception"""
from typing import List, ClassVar
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


def build(v: int) -> C:
    return C(v)


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    c = build(-1)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
