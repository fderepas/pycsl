"""WL-04b — same defect for `List[float]`: `let f (a: array int) ... : real = a[i]`
(int vs real). TYPEERR."""
_ = 0
from typing import List
def f(a: List[float], i: int) -> float:
    return a[i]
