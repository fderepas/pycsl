"""WL-04 COLLAPSED/WRONG-REPR — `List[str]`/`List[float]` element read collapses to
`int` (array int) but the use site is faithfully typed (str/real return), producing
INTERNALLY-INCONSISTENT, ill-typed WhyML: `let f (a: array int) ... : string = a[i]`
(a[i] : int vs return : string).

Detector D2: TYPEERR. A legitimate function reading a str/float list element is
REJECTED — the element-opaque collapse collides with a faithful element type
instead of either a faithful read or a clean diagnostic."""
_ = 0
from typing import List
def f(a: List[str], i: int) -> str:
    return a[i]
