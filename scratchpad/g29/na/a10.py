r"""G29 NA10 — negative index -1 on a list after pop."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    lst: List[int] = [1, 2, 3]
    lst.pop()
    return lst[-1]


if __name__ == "__main__":
    print("CPython:", probe())
