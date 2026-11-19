r"""G29 NE-M1 — no_exception ValueError on a builtin that raises it."""
import math
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    return int(math.sqrt(-1.0))


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
