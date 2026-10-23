r"""Q3 — a module's own `__dict__` mutated by a method call at module scope."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

plainlib.__dict__.update({"inc": plainlib.dec})


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
