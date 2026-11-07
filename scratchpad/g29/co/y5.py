r"""G29 CO-Y5 — the empty-list placeholder in other consumers."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    return [][0]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
