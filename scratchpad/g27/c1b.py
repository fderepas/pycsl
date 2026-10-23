r"""C1b — C1 again with a CONSTANT getattr name (the `"set" + "attr"` BinOp made the first
attempt fail on a lowering error, not on a fence): a def BODY is outside the module-executed
region and the def is CALLED at module scope."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib
import builtins


def g() -> None:
    sa = getattr(builtins, "setattr")
    sa(plainlib, "inc", plainlib.dec)


g()


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
