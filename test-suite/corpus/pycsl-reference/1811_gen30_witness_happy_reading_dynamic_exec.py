r"""Test 1811 — WITNESS: a `#@ happy ... reads ... outside region` policy refuses a
non-exempt method containing a DYNAMIC `exec(...)`.

The sibling refusal one branch over — the WRITING policy's "may write anything" — already
had a witness; this one, the READING policy's "may read anything", did not.

IT IS NOT REACHED BY A CONSTANT `exec`. `splice_constant_exec` replaces a
compile-time-constant `exec("...")` with its parsed straight-line body BEFORE the weaver
runs, so no `exec` Call node survives for the policy check to find — measured: the same
file with `exec("y = 1")` verifies. The exec must be DYNAMIC (`exec(s)` over a parameter)
for the refusal to have anything to see. Lesson (n3): an earlier pass can retire a later
check just as surely as an earlier refusal can.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy conf:
#@     region 0 .. 4 reads self.secret outside region
#@     except reader

#@ class invariant \length(self.secret) >= 8
class S:
    def __init__(self) -> None:
        self.secret: list = [0] * 8

    #@ assigns \nothing
    def reader(self) -> int:
        return self.secret[0]

    #@ assigns \nothing
    def peeker(self, s: str) -> int:
        exec(s)
        return 0
