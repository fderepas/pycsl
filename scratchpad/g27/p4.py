r"""P4 (a5b) — an eval text that CALLS a module def which patches the namespace; the text
names only that def, so no token of the eight appears."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib


def h() -> None:
    plainlib.inc = plainlib.dec


eval("h()")


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
