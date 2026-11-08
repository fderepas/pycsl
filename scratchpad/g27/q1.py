r"""Q1 — the computed-getattr arm keys on the SHAPE `Call(func=Call(getattr,...))`. Bind the
result to a name first and the shape never appears (generator #9, on gen #26's own arm)."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib
import builtins

sa = getattr(builtins, "set" + "attr")
sa(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
