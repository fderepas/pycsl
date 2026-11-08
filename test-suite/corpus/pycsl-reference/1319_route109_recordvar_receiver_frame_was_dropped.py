r"""Test 1319 — ROUTE #109 negative: the `#32 SPIKE` `_objstate_w` frame fallback existed in the
`self.` arm of `_resolve_dotted_signature` only. A RECORD-VARIABLE receiver `c.bump()`, whose
callee declares `#@ assigns self.hidden` on a field that is not an emitted record label, got an
avatar with NO frame and NO receiver (`val c_bump_0 () : unit`), so `#@ assigns \nothing`
PROVED while `bump` writes `c.hidden`. The avatar is now `val c_bump_0 (self: c) : unit
writes { _pyobj_state }` and the frame is refused. Positive twin: 1320.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL


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
