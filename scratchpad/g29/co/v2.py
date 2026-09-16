r"""G29 CO-V2 — route #159 POSITIVE control (lit): an in-range index under no_exception IndexError must still prove."""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = [1, 2]
    return xs[1]
