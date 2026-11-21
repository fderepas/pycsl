r"""Test 1456 - ROUTE #147: the ancestor that OWNS the inherited constructor is IMPORTED
from another module, so the copy must happen after cross-module import resolution has put
the base's record into `records`. `Cee(7).get()` is 7 and PROVES; it FAILED before the repair.
"""
_ = 0  # anchor
from multi_file_lib.r147_ctorbase import Ay


class Cee(Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
