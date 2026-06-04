"""Test 0461 — HAPPY trust boundary (theorem clause 2), positive case.

`ext_scrub` is `\trusted` (its body is not verified) and is NOT in the exempt set,
so it could in principle write the reserved region [512, 2560). It opts into the
trust boundary with `#@ \preserves`: the meta-pass then synthesizes and attaches the
canonical region-preservation postcondition
    ensures \forall i; (512 <= i and i < 2560) ==> self.disk[i] == \old(self.disk[i])
which callers may ASSUME. With the promise present the file verifies. Contrast 0462,
where omitting `#@ \preserves` is a hard error — the clause has teeth.
"""
_ = 0  # anchor
#@ class invariant \length(self.disk) >= 4096
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_meta
class Store:
    def __init__(self) -> None:
        self.disk: list = bytearray(4096)

    #@ \trusted reviewer: demo
    #@ \preserves
    def ext_scrub(self, x: int) -> None:
        self.disk[3000] = x            # outside the region; body trusted, not checked

    #@ requires 0 <= off and off < 4096
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v             # exempt: legitimate region writer
