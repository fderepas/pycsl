r"""G29 IE-U3 — tuple unpack into a subscript target."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0, 0]
    a, xs[0] = 1, 5
    return xs[0]
if __name__ == "__main__":
    print("CPython:", probe())
