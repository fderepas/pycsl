r"""G29 NE-N6 — no_exception ValueError on a shape that raises it."""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    xs: List[int] = [1]
    return xs.index(5)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
