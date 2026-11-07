r"""getattr with a default on a missing attribute"""
from typing import List, Dict, Any
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = 7


#@ ensures \result == 7
def probe() -> int:
    c = C()
    return getattr(c, "w", 3)


if __name__ == "__main__":
    print("CPython:", probe())
