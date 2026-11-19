r"""None in a tuple literal"""
from typing import List, Dict, Optional, Set, Tuple
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    t: Tuple[Optional[int], int] = (None, 1)
    return t[0] == 0


if __name__ == "__main__":
    print("CPython:", probe())
