r"""None field truthiness"""
from typing import List, Dict, Optional, Tuple
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v: Optional[int] = None


#@ ensures \result == 1
def probe() -> int:
    c = C()
    if c.v:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
