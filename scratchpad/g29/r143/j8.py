r"""G29 J8 — route #143 control: the importer imports LIM FROM THE SAME MODULE; no refusal."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f, LIM


#@ assigns \nothing
#@ ensures \result == k - 1
def caller(k: int) -> int:
    return k + LIM
