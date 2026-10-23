r"""G29 CO-Y4 — the empty-list placeholder in other consumers."""
from typing import List
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    xs: List[int] = []
    return len(sorted(xs))


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
