r"""G29 NE-P2 — no_exception ValueError on a shape that raises it (carrier-rerun on #159/#160)."""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    b = bytes(-1)
    return len(b)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
