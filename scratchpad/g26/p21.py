r"""P21 — #135 carrier: a module-scope patch inside a COMPREHENSION on a fresh-looking name."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

_junk = [setattr(m, "inc", plainlib.dec) for m in [plainlib]]


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
