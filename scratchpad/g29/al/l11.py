r"""G29 AL-l11 — a slice assignment that SHRINKS the list."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    a: List[int] = [1, 2]
    a[0:2] = [9]
    return len(a)


if __name__ == "__main__":
    print("CPython:", probe())
