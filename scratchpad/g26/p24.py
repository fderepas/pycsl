r"""P24 — #135 carrier: CLASS-BODY lambda doing the patch."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib


class K:
    _j = (lambda m: setattr(m, "inc", plainlib.dec))(plainlib)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
