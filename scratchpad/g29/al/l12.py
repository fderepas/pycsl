r"""G29 AL-l12 — a slice assignment that GROWS the list, read past the old element."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 8
def probe() -> int:
    a: List[int] = [1, 2]
    a[0:1] = [7, 8]
    return a[1]


if __name__ == "__main__":
    print("CPython:", probe())
