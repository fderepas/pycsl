# pycsl-flags: --memory-model hoare
"""PROBE 232 — the `<recordvar>.m()` ARM (the arm the #32 repair did NOT reach).
Identical callee. The 6-tuple field_spec at expressions.py:6700 computes `writes` with the
SAME `_writes_filtered_to_labels` filter but NEVER computes `_objstate_w`, so when the filter
empties the set the gate `if field_ens or writes or frame_ens or result_frame_ens:` is FALSE,
field_spec is None, and the call lowers to an abstract op with NO FRAME.
If `#@ assigns \nothing` PROVES here while it FAILS in self_arm.py, the route is LIVE.
"""


class C:
    def __init__(self) -> None:
        self.a = 0

    #@ assigns self.hidden
    def bump(self) -> None:
        self.hidden = 5


#@ assigns \nothing
#@ ensures \result == 0
def caller() -> int:
    c = C()
    c.bump()
    return c.a
