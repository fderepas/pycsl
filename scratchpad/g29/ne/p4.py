r"""G29 NE-P4 — no_exception ValueError on a shape that raises it (carrier-rerun on #159/#160)."""
import math
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    return math.factorial(-1)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
