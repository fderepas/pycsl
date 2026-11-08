"""1192 — ROUTE #76: the constructor ONE CALL DEEPER, which refuted a blocklist guard.

The obvious repair — "refuse when the function body CONSTRUCTS an instance" — was written
out, measured, and REFUTED BEFORE A LINE OF IT LANDED. Here `dup`'s body contains no
constructor at all; the construction happens inside `mk`, one call deeper. The false
`\\result == x` still PROVED. That is the seventh time this campaign has recorded "a guard
keyed on a syntactic location is defeated by moving the hazard one step", and the second
time it was caught BEFORE landing rather than after.

The lesson that came out of it is the one worth keeping: an ALLOWLIST keyed on syntax
fails CLOSED when the hazard moves, whereas a BLOCKLIST fails OPEN. #76's repair is
therefore an allowlist — `dup` is refused here not because a constructor was spotted, but
because its returns do not match the compared read path.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


class C:
    v: int

    def __init__(self, v: int) -> None:
        self.v = v


#@ assigns \nothing
def mk(n: int) -> C:
    return C(n)


#@ ensures \result == x
#@ assigns \nothing
def dup(x: C) -> C:
    return mk(x.v)
