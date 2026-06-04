"""Test 0459 — HAPPY meta-property: region integrity over a shared field.

A single module-level `#@ happy` declares that the reserved region [512, 2560)
of `self.disk` may be written ONLY by the allowlisted method `_write_meta`. The
meta-pass (meta.md Stage B) expands this into a per-site `#@ check` at every write
of `self.disk` in every other method. Here all such writes are provably outside
the region (point and slice), so the file verifies. The exempt method gets no
obligation.

One declaration replaces a disjoint-region obligation hand-copied into every
non-exempt write site.
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

    #@ requires 0 <= i and i < 512
    def set_bitmap(self, i: int, v: int) -> None:
        self.disk[i] = v                                   # point, below region

    #@ requires block >= 5 and block < 8
    #@ requires \length(data) == 512
    def write_block(self, block: int, data: list) -> None:
        self.disk[block * 512 : block * 512 + 512] = data  # slice, at/above region

    #@ requires 0 <= off and off < 4096
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v                                 # exempt: no obligation
