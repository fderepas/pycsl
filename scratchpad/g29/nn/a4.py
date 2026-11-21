r"""None in a set literal"""
from typing import List, Dict, Optional, Set, Tuple
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    s: Set[Optional[int]] = {None}
    return 0 in s


if __name__ == "__main__":
    print("CPython:", probe())
