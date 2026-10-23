r"""G29 NE-M9 — no_exception ValueError on a builtin that raises it."""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    return int("12", 1)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
