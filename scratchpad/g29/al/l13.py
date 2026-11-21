r"""G29 AL-l13 — control: an EQUAL-length slice assignment keeps its faithful model."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 8
def probe() -> int:
    a: List[int] = [1, 2]
    a[0:2] = [7, 8]
    return a[1]


if __name__ == "__main__":
    print("CPython:", probe())
