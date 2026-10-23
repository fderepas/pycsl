r"""G29 NA7 — del lst[0] shifts elements."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    lst: List[int] = [1, 2, 3]
    del lst[0]
    return lst[0]


if __name__ == "__main__":
    print("CPython:", probe())
