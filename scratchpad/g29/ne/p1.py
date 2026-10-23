r"""G29 NE-P1 — no_exception IndexError on a shape that raises it (carrier-rerun on #159/#160)."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs = [[1]]
    return xs[0][5]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
