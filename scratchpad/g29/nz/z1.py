r"""None field is not None test"""
from typing import List, Dict, Optional, Tuple
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v: Optional[int] = None


#@ ensures \result == True
def probe() -> bool:
    c = C()
    return c.v is not None


if __name__ == "__main__":
    print("CPython:", probe())
