r"""G29 NE-P7 — no_exception KeyError on a shape that raises it (carrier-rerun on #159/#160)."""
from typing import List
_ = 0  # anchor


#@ no_exception KeyError
def probe() -> int:
    d = {1: 2}
    return d.pop(5)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
