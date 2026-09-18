r"""property on module-level class used as attribute"""
from typing import Callable, List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self._v = 2

    @property
    def v(self) -> int:
        return self._v * 3


#@ ensures \result == 2
def probe() -> int:
    c = C()
    return c.v


if __name__ == "__main__":
    print("CPython:", probe())
