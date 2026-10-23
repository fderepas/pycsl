r"""None assigned to a field after construction"""
from typing import List, Dict, Optional, Set, Tuple
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v: Optional[int] = 1


#@ ensures \result == True
def probe() -> bool:
    c = C()
    c.v = None
    return c.v == 0


if __name__ == "__main__":
    print("CPython:", probe())
