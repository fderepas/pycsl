r"""G29 CO-Y7 — a NON-empty literal list indexed out of range under no_exception IndexError (control of the bounds VC)."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = [1, 2]
    return xs[5]
