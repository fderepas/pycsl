r"""G29 CO-Y9 — a STORE into the empty list under no_exception IndexError."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    xs[0] = 5
    return 1


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
