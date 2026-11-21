r"""G29 AL-L10 — slice assignment that GROWS a list, no alias."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    a: List[int] = [1, 2]
    a[2:] = [3, 4]
    return len(a)


if __name__ == "__main__":
    print("CPython:", probe())
