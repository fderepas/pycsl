r"""setattr then read"""
from typing import List, Dict, Any
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = 0


#@ ensures \result == 0
def probe() -> int:
    c = C()
    setattr(c, "v", 5)
    return c.v


if __name__ == "__main__":
    print("CPython:", probe())
