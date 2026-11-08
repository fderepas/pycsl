r"""G29 IE-J10 — a list index error in a helper, caught by the caller."""
from typing import List
_ = 0  # anchor


def get(xs: List[int]) -> int:
    return xs[5]


#@ ensures \result == 0
def probe() -> int:
    try:
        v = get([1])
    except IndexError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
