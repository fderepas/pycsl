r"""G29 CO-Z13 — `all` over a list built by append whose appended element FAILS the predicate."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    xs: List[int] = []
    xs.append(-1)
    return 1 if all(x >= 0 for x in xs) else 0


if __name__ == "__main__":
    print("CPython:", probe())
