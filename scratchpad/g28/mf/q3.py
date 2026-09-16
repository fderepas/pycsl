r"""Q3 — carrier-rerun on route #147: the ancestor that owns the inherited constructor is
IMPORTED from another module."""
_ = 0  # anchor
from q3lib import Ay


class Cee(Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
