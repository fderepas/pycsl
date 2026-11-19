r"""G29 IE-G3 — `ensures True` helper, but a loop invariant claim inside."""
from typing import List
_ = 0  # anchor


#@ ensures True
def f() -> int:
    xs: List[int] = []
    r = 0
    try:
        r = xs[0]
    except IndexError:
        r = 9
    i = 0
    #@ loop invariant r == 0
    #@ loop variant 3 - i
    while i < 3:
        i = i + 1
    return r


if __name__ == "__main__":
    print("CPython:", f())
