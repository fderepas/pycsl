r"""G29 NE-M2 — no_exception ValueError on a builtin that raises it."""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    s = "abc"
    return s.index("z")


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
