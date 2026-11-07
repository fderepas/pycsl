r"""G29 CO-V4 — route #159 POSITIVE control (mul): an in-range index under no_exception IndexError must still prove."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = [0] * 3
    xs[2] = 5
    return xs[2]
