r"""G29 IE-G1 — an uncontracted helper with a handled placeholder read; the caller claims the value."""
from typing import List
_ = 0  # anchor


def f() -> int:
    xs: List[int] = []
    try:
        v = xs[0]
    except IndexError:
        return 9
    return v * 0


#@ ensures \result == 0
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
