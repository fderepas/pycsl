r"""computed attribute name"""
from typing import List, Dict, Any
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = 7


#@ ensures \result == 0
def probe() -> int:
    c = C()
    name = "v"
    return getattr(c, name)


if __name__ == "__main__":
    print("CPython:", probe())
