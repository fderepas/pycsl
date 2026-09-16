r"""G29 CO-V3 — route #159 POSITIVE control (append): an in-range index under no_exception IndexError must still prove."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    xs.append(7)
    return xs[0]
