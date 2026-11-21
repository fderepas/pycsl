r"""comprehension tuple target wrong arity"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    rows: List[List[int]] = [[1, 2, 3]]
    ys = [a for a, b in rows]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
