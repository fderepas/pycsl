r"""StopIteration caught from next on empty iterator"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    try:
        v = next(iter(xs))
    except StopIteration:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
