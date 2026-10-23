r"""G29 NE-N10 — no_exception ZeroDivisionError on a shape that raises it."""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception ZeroDivisionError
def probe() -> int:
    x = 5.0
    return int(x / 0)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
