r"""G29 NA9 — list.remove removes only the first occurrence."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    lst: List[int] = [3, 1, 3]
    lst.remove(3)
    return lst.count(3) + 1


if __name__ == "__main__":
    print("CPython:", probe())
