r"""G29 K11 — route #143 positive control: the importer imports LIM FROM THE SAME MODULE as the
callee, so the name denotes the same binding in both scopes; the tagged contract is allowed and
the precondition `0 >= LIM` folds to `0 >= -1`."""
_ = 0  # anchor
from multi_file_lib.r143_reqlib import g2, LIM


#@ ensures \result == 0
#@ assigns \nothing
def caller() -> int:
    return g2(0)
