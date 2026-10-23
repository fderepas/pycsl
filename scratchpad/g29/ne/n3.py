r"""G29 NE-N3 — no_exception ZeroDivisionError on a shape that raises it."""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception ZeroDivisionError
def probe() -> int:
    x = 5
    y = 0
    return x % y


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
