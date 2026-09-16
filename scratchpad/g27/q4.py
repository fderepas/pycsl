r"""Q4 — `type(...)` and the `__setattr__` slot: neither spelling is in `_nb_ns_builtins`."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

type(plainlib).__setattr__(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
