r"""for tuple target over rows of wrong arity"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    rows: List[List[int]] = [[1, 2, 3]]
    for a, b in rows:
        pass
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
