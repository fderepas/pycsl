r"""G29 NE-Q5 — a subscript on a dict returned by a CALL under no_exception KeyError."""
from typing import Dict
_ = 0  # anchor


#@ assigns \nothing
def mk() -> Dict[int, int]:
    return {1: 2}


#@ no_exception KeyError
def probe() -> int:
    return mk()[5]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
