r"""G29 CH3 — chained assignment to a LIST element as the second target."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def f() -> int:
    xs: List[int] = [1, 2]
    a = xs[0] = 5
    return xs[0]


if __name__ == "__main__":
    print("CPython:", f())
