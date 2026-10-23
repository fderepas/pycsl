r"""Test 1320 — ROUTE #109 positive twin: the same call under an HONEST caller frame
(`#@ assigns c.hidden`) proves `\result == 0`, the caller emitted with
`writes { _pyobj_state }`. Negative: 1319.
"""
# pycsl-flags: --memory-model hoare


class C:
    def __init__(self) -> None:
        self.a = 0

    #@ assigns self.hidden
    def bump(self) -> None:
        self.hidden = 5


#@ assigns c.hidden
#@ ensures \result == 0
def caller() -> int:
    c = C()
    c.bump()
    return c.a
