r"""None element arithmetic"""
from typing import List, Dict, Optional, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[Optional[int]] = [None]
    v = xs[0]
    return v + 1


if __name__ == "__main__":
    print("CPython:", probe())
