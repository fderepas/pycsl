"""Advice probe (route #549, PYCSL-R549-NONE-ARGUMENT): 'Narrow it first (`if v is not None:` ...)' --
witness g1313_bn1210 (`v = None; return g(v)` of an imported `def g(x: int)`) with `v` possibly rebound to
`k` and the call under `if v is not None:`. VERIFIES under `no_exception \\all`."""
from typing import Optional
from rt52dep import g


#@ no_exception \all
def f(k: int) -> int:
    v: Optional[int] = None
    if k > 0:
        v = k
    if v is not None:
        return g(v)
    return 0


if __name__ == "__main__":
    print("result", f(1), f(0))
