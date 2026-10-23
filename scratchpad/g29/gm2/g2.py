r"""global instance constructed with raising init"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    return 0


_g = C(-1)


if __name__ == "__main__":
    print("CPython:", probe())
