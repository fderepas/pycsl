# pycsl-flags: --memory-model hoare
"""PROBE 232 — the `self.` ARM (the arm that GOT the #32 `_objstate_w` repair).
A sibling method calls `self.bump()`, whose declared `#@ assigns self.hidden` names a field
the record does not carry as an emitted label. The 7-tuple field_spec at expressions.py:6660
sets `_objstate_w`, so the avatar is framed on `_pyobj_state` and the caller's
`#@ assigns \nothing` must FAIL. This is the CONTROL: it shows the obligation is live.
"""


class C:
    def __init__(self) -> None:
        self.a = 0

    #@ assigns self.hidden
    def bump(self) -> None:
        self.hidden = 5

    #@ assigns \nothing
    #@ ensures \result == 0
    def go(self) -> int:
        self.bump()
        return self.a
