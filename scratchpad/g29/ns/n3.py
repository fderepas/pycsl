r"""None in list element"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    xs: List[Optional[int]] = [None]
    return xs[0] == 0


if __name__ == "__main__":
    print("CPython:", probe())
