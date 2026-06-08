"""Test 0652 — Gap 7 (gap7-spec-rev2): void/mutating method call on a record-instance local.

`c = Counter(); c.inc(); return c.x` proves `\result == 1`. Previously `c.inc()` lowered to an opaque
`val c_inc_0 () : unit` (no self, no writes, no ensures) — a no-op — so c was never mutated. Now the
call resolves the receiver's class and emits `val c_inc_0 (self: counter) : unit writes { self.x }
ensures { self.x = old self.x + 1 }` and calls `(c_inc_0 c)`, so c.x is mutated through the abstract
op's frame. The real `counter__inc` is still emitted + verified (a false ensures fails IT, not the
caller).
"""


class Counter:
    #@ assigns self.x
    #@ ensures self.x == 0
    def __init__(self) -> None:
        self.x: int = 0

    #@ assigns self.x
    #@ ensures self.x == \old(self.x) + 1
    def inc(self) -> None:
        self.x = self.x + 1


#@ ensures \result == 1
#@ assigns \nothing
def driver() -> int:
    c = Counter()
    c.inc()
    return c.x
