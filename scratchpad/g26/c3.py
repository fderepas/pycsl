r"""C3 — carrier: `object.__setattr__` instead of `setattr`."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

object.__setattr__(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
