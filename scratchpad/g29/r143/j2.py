r"""G29 J2 — route #143 control: no importer binding of LIM; must stay REFUSED by the proof
(unconstrained `val constant`), never by the #143 check."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)
