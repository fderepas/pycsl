r"""P9 — #136 widen: DYNAMIC exec rebinding an IMPORTED name at module scope."""
_ = 0  # anchor
from multi_file_lib.r119_plainlib import inc
from multi_file_lib.r119_plainlib import dec

exec("in" + "c = dec")


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
