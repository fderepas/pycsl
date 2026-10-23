r"""None appended to a list"""
from typing import List, Dict, Optional, Set, Tuple
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    xs: List[Optional[int]] = []
    xs.append(None)
    return xs[0] == 0


if __name__ == "__main__":
    print("CPython:", probe())
