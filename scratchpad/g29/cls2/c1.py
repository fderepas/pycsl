r"""classmethod factory with raising init caught"""
from typing import List, ClassVar
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v

    @classmethod
    def make(cls, v: int) -> "C":
        return cls(v)


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C.make(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
