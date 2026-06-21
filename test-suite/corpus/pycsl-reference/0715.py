"""Test 0715 — HAPPY H-I1: read confinement over a reserved region (positive).

`#@ happy key_confine: region 0 .. 64 reads self.disk outside region except _read_key`
declares that the key bytes [0, 64) of `self.disk` may be READ only by `_read_key`. The
meta-pass (the read mirror of the H-T region form) expands this into a per-READ-site
`#@ check (idx < 0 or idx >= 64)` in every non-exempt method. Here the formatter only reads
at/above the region, so every read-confinement check is provably outside [0, 64) and the
file verifies. The exempt reader gets no obligation. The C sibling (macsl) expresses the
same property as `\context(\reading)` (see happy-roadmap-impl.md §0a).
"""
# pycsl-flags: --memory-model hoare
#@ class invariant \length(self.disk) >= 4096
#@ happy key_confine:
#@     region 0 .. 64
#@     reads self.disk outside region
#@     except _read_key
class Store:
    def __init__(self) -> None:
        self.disk: list = bytearray(4096)

    #@ requires 64 <= off and off < 4096
    def format_entry(self, off: int) -> int:
        return self.disk[off]            # point read at/above region — provably outside [0,64)

    #@ requires 1 <= n and n < 64
    def tail_sum(self, n: int) -> int:
        return self.disk[64] + self.disk[64 + n]   # two reads, both >= 64 — outside

    #@ requires 0 <= off and off < 64
    def _read_key(self, off: int) -> int:
        return self.disk[off]            # exempt legitimate reader — no obligation
