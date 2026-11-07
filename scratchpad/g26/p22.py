r"""P22 — #135 carrier: a lambda BOUND at module scope and called at module scope."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

patch = lambda: setattr(plainlib, "inc", plainlib.dec)
patch()


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
