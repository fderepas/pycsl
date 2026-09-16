r"""G29 NE-M7 — no_exception ValueError on a builtin that raises it."""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    x, y = [1, 2, 3]
    return x


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
