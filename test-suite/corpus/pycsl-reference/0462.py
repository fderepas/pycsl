"""Test 0462 — HAPPY trust boundary (theorem clause 2), teeth.

Identical to 0461 except `ext_scrub` OMITS `#@ \preserves`. It is `\trusted` (body
unverified) and not exempt, so the meta-pass cannot certify that it leaves the
reserved region untouched, and there is no body site to check. Per the composition
theorem, an undeclared trusted writer breaks whole-program soundness, so the meta-pass
rejects the program with a hard error (rather than silently over-claiming). This proves
clause 2 has teeth: trust must be made explicit.
"""
# pycsl-expected: FAIL
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
    def ext_scrub(self, x: int) -> None:
        self.disk[3000] = x            # no `#@ \preserves` -> hard error

    #@ requires 0 <= off and off < 4096
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v
