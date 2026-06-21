"""Test 0717 — negative: aliasing the protected base to evade read confinement is rejected (H-I1).

`sneaky` aliases `x = self.disk` then reads `x[off]` — a read through the alias would evade
the per-read-site check. The meta-pass rejects the alias as a hard semantic error
(sound-by-rejection), closing the evasion the per-site check alone would miss.
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
    def sneaky(self, off: int) -> int:
        x = self.disk                    # alias the protected base -> hard error
        return x[off]

    #@ requires 0 <= off and off < 64
    def _read_key(self, off: int) -> int:
        return self.disk[off]
