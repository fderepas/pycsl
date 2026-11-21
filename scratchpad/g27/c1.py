r"""C1 — carrier of MY OWN draft-1: the getattr arm is module-executed only, and a def BODY
is still outside that region. The def is CALLED at module scope."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib
import builtins


def g() -> None:
    sa = getattr(builtins, "set" + "attr")
    sa(plainlib, "inc", plainlib.dec)


g()


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
