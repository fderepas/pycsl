"""Test 0716 — negative: a non-exempt method READING the protected key region is caught (H-I1).

Same HAPPY as 0715, but `leak_key` (NOT exempt) reads `self.disk[off]` with `0 <= off < 64`,
i.e. INSIDE the reserved region. The meta-pass injects `#@ check (off < 0 or off >= 64)` at
that read, which is unprovable (the read is in-region) — surfacing the read-confinement
violation as an unproven VC. (The macsl twin is attacks.c's confidentiality red.)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ class invariant \length(self.disk) >= 4096
#@ happy key_confine:
#@     region 0 .. 64
#@     reads self.disk outside region
#@     except _read_key
class Store:
    def __init__(self) -> None:
        self.disk: list = bytearray(4096)

    #@ requires 0 <= off and off < 64
    def leak_key(self, off: int) -> int:
        return self.disk[off]            # reads INSIDE [0,64) in a non-exempt method -> check fails

    #@ requires 0 <= off and off < 64
    def _read_key(self, off: int) -> int:
        return self.disk[off]
