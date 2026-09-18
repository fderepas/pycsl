r"""G29 NA8 — list.insert at an index past the end appends."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 9
def probe() -> int:
    lst: List[int] = [1, 2]
    lst.insert(10, 5)
    return lst[2] + len(lst)


if __name__ == "__main__":
    print("CPython:", probe())
