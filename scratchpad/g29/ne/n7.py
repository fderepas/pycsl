r"""G29 NE-N7 — no_exception StopIteration on a shape that raises it."""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception StopIteration
def probe() -> int:
    return next(iter([]))


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
