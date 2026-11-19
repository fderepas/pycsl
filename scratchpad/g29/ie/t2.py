r"""AttributeError caught on None"""
from typing import List, Dict, Optional
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == 0
def probe() -> int:
    c: Optional[C] = None
    try:
        v = c.x
    except AttributeError:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
