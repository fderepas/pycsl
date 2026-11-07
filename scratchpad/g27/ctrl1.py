r"""CTRL1 — positive control for P1/P4: the plain module-scope setattr spelling IS refused."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

plainlib.inc = plainlib.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
