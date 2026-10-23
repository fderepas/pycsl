r"""G29 NE-M4 — no_exception ValueError on a builtin that raises it."""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    t = 0
    for i in range(0, 5, 0):
        t = t + 1
    return t


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
