r"""G29 NE-N2 — no_exception KeyError on a shape that raises it."""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception KeyError
def probe() -> int:
    return {}[1]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
