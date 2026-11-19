r"""G29 CO-Y6 — the empty-list placeholder in other consumers."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    xs: List[int] = []
    t = 0
    for x in xs:
        t = t + 1
    return t


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
