r"""G29 CO-Y11 — a TUPLE index past its end under no_exception IndexError."""
from typing import Tuple
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    t = (1, 2)
    return t[5]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
