r"""set remove missing caught"""
from typing import Dict, List, Set
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: Set[int] = {1}
    try:
        s.remove(2)
    except KeyError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
