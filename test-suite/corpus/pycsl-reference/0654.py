"""Test 0654 — Gap 7 P3 (gap7-spec-rev2): void/mutating method called via `self.<m>()` from a sibling.

`inc2` calls `self.inc()` twice; each must mutate `self.x` (+1) so `inc2` proves `self.x == \old+2`.
Previously `self.inc()` lowered to opaque `val self_inc_0 () : unit` (no self/writes) → no-op → inc2
failed. The `self.`-branch now folds in the method's `writes`/`\old`-ensures and emits
`val self_inc_0 (self: c) : unit writes { self.x } ensures { self.x = old self.x + 1 }`, passing the
enclosing `self` — so the sibling-call mutation is visible.
"""


class C:
    #@ assigns self.x
    #@ ensures self.x == 0
    def __init__(self) -> None:
        self.x: int = 0

    #@ assigns self.x
    #@ ensures self.x == \old(self.x) + 1
    def inc(self) -> None:
        self.x = self.x + 1

    #@ assigns self.x
    #@ ensures self.x == \old(self.x) + 2
    def inc2(self) -> None:
        self.inc()
        self.inc()
