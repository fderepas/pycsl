r"""None stored by subscript"""
from typing import List, Dict, Optional, Set, Tuple
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    xs: List[Optional[int]] = [1]
    xs[0] = None
    return xs[0] == 0


if __name__ == "__main__":
    print("CPython:", probe())
