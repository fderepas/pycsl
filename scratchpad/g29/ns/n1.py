r"""None field read as zero"""
from typing import List, Dict, Optional
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v: Optional[int] = None


#@ ensures \result == True
def probe() -> bool:
    c = C()
    return c.v == 0


if __name__ == "__main__":
    print("CPython:", probe())
