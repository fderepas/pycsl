r"""None local arithmetic"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    x: Optional[int] = None
    return x + 1


if __name__ == "__main__":
    print("CPython:", probe())
