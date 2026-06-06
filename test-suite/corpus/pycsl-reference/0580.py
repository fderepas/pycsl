"""Test 0580 — negative: a recursive method on a global is refused for inlining (Phase 3).

`Counter.loop` calls itself. Inlining a recursive method would not terminate, so the
inliner refuses with a hard error — such a method must be verified by contract + a
`#@ \variant`, not by inlining. Demonstrates the recursion guard (soundness, not a nicety).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare

#@ class invariant self.n >= 0
class Counter:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def loop(self) -> None:
        self.loop()


cnt = Counter()


#@ assigns cnt.n
def go() -> None:
    cnt.loop()
