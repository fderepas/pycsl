r"""G29 NA1 — `[[0]*2]*2` shares the inner row: writing grid[0][0] changes grid[1][0]."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    grid: List[List[int]] = [[0] * 2] * 2
    grid[0][0] = 7
    return grid[1][0]


if __name__ == "__main__":
    print("CPython:", probe())
