# ROUTE #221 CONTROL (expects FAILED under `--fun use` — the TRUE twin).
#
# `enter` writes `self.v = 7` and declares NO `#@ assigns`. The emitter SYNTHESIZES the
# frame `ensures { self.v = old self.v }` from that absence, the call site ASSUMES it, and
# `--fun use` never proves the callee, so nothing ever checks it. CPython answers -7.
#
# Run the same file WITHOUT `--fun` and it fails, because the callee's own frame goal is
# then discharged and does not hold. The flag is what makes the claim false.
_ = 0  # anchor


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    def enter(self) -> int:
        self.v = 7
        return 0


#@ ensures \result == -7
def use() -> int:
    c = C()
    before: int = c.v
    _r: int = c.enter()
    after: int = c.v
    return before - after
