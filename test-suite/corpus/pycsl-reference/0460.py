"""Test 0460 — HAPPY teeth: a non-exempt write INTO the reserved region must FAIL.

`stray` is not in the exempt set, yet it writes `self.disk[1000]` — index 1000 lies
inside the reserved region [512, 2560). The meta-pass injects `#@ check 1000 < 512
or 1000 >= 2560` at that site, which is unprovable, so verification fails AT THAT
SITE. This proves the HAPPY obligation has teeth (contrast 0459, which proves). A
per-method contract alone would not have caught this cross-cutting violation.
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

    def stray(self, v: int) -> None:
        self.disk[1000] = v               # inside [512, 2560) -> injected check fails

    #@ requires 0 <= off and off < 4096
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v
