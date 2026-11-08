# pycsl-flags: --memory-model hoare
_ = 0  # anchor
import multi_file_lib.probelib


#@ ensures \result > 0
#@ assigns \nothing
def f() -> int:
    return multi_file_lib.probelib.pos_only(-5)
