r"""C4 — carrier: the module's `__dict__` written by subscript."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

plainlib.__dict__["inc"] = plainlib.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
