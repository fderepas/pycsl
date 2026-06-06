"""0426 — slice-read has real Array.sub semantics (length + content).

A slice `self.disk[a:b]` on a known `array int` source now lowers to Why3's
`Array.sub` (`length result = b-a`, `result[i] = disk[a+i]`), so reading back a
just-written element is provable. (Previously the slice was an opaque
`array_slice` val with no axioms, and this could not be proven.)
"""

DISK = 131072


#@ class invariant \length(self.disk) >= 131072
class SliceRead:
    def __init__(self):
        self.disk: list = bytearray(DISK)

    #@ requires 0 <= base and base + 4 <= 131072
    #@ requires 0 <= v and v < 256
    #@ assigns self.disk
    #@ ensures \result == v
    def write_then_read_first(self, base: int, v: int) -> int:
        self.disk[base] = v
        chunk = self.disk[base:base + 4]   # Array.sub self.disk base 4
        return chunk[0]                    # = self.disk[base] = v
