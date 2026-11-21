r"""G29 NE-M8 — no_exception ZeroDivisionError on a builtin that raises it."""
from typing import List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
def probe() -> int:
    return pow(0, -1)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
