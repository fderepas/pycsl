r"""G29 NE-N5 — no_exception IndexError on a shape that raises it."""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    return xs.pop()


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
