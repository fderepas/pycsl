r"""getattr with a literal name"""
from typing import List, Dict, Any
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = 7


#@ ensures \result == 0
def probe() -> int:
    c = C()
    return getattr(c, "v")


if __name__ == "__main__":
    print("CPython:", probe())
