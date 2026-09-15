r"""C2 — carrier: `setattr` reached through an ALIAS, so the sink spelling misses it."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

sa = setattr
sa(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
