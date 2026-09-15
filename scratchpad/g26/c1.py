r"""C1 — carrier of my #137 draft: the receiver has NO module-scope binding (default fresh)
because it is bound by a `global` write in a function called at module scope."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib


def s() -> None:
    global m
    m = plainlib


s()
m.inc = plainlib.dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
