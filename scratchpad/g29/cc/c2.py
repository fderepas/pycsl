r"""bool in dict key collision"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    d: Dict[int, int] = {1: 1}
    d[True] = 2
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
