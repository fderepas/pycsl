r"""P20 — #135 carrier: the module-scope patch hidden in a LAMBDA BODY (the sink walk
skips Lambda; #119 rule (6) exempts a parameter receiver)."""
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib

(lambda m: setattr(m, "inc", plainlib.dec))(plainlib)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
