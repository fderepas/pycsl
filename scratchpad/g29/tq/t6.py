r"""tuple comparison in sorted keys"""
from typing import List, Tuple, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    ps: List[Tuple[int, int]] = [(2, 1), (1, 2)]
    ps.sort()
    return ps[0][0]


if __name__ == "__main__":
    print("CPython:", probe())
