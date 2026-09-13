# pycsl-flags: --check-behavioral-subtyping
# pycsl-expected: FAIL
"""1276 — (#49) ROUTE #97, THE NON-REGRESSION CELL. The FIELDED base that ALREADY worked.

0445 is the in-tree positive control for `--check-behavioral-subtyping`, but the suite
runs it WITHOUT the flag (it carries no `# pycsl-flags:` header), so only an agent-test
exercises the check. This witness bakes the flag in, so the arm that was ALREADY correct
before route #97 is enforced by the reference suite itself: the repair split one loop into
two jobs, and this file is what turns red if the split ever loses the fielded path.
"""


#@ class invariant self.v >= 0
class Base:
    def __init__(self):
        self.v: int = 0

    #@ requires x >= 0
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x + self.v


class Sub(Base):
    #@ requires x >= 5
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x + self.v
