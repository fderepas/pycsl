r"""J1 — carrier of MY OWN #141 repair: the rule permits a MODULE GLOBAL in a `raises`
condition because it denotes the same object in both scopes. That is only true WITHIN a module:
an IMPORTED callee's condition names ITS module's global, rendered in the CALLER's."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)
