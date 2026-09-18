r"""nested comprehension inner subscript"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    g: List[List[int]] = [[1]]
    s = [[r[1] for _ in [0]] for r in g]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
