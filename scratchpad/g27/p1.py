r"""P1 (a4) — `_nb_imported` is file-wide by NAME: a LOCAL bound to the builtins module
is not in it, so `getattr(b, "setattr")(...)` escapes the computed-getattr callee arm."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib
import builtins

b = builtins
getattr(b, "set" + "attr")(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
