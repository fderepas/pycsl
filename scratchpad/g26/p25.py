r"""P25 — #135: a module patched through a `from pkg import mod` binding."""
_ = 0  # anchor
from multi_file_lib import r119_plainlib as pl

pl.inc = pl.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return pl.inc(3)
