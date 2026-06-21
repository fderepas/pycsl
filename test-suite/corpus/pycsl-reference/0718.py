"""Test 0718 — negative: a non-exempt trusted reader has no checkable body, so it is rejected (H-I1).

`opaque_reader` is `\trusted` (no body) and NOT exempt — it could read the protected region
with no per-site check to constrain it. The meta-pass rejects this as a hard error: a
trusted/abstract reader of a read-confined field must be listed in `except`.
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

    #@ \trusted reviewer: happy-impl
    #@ requires 0 <= off and off < 4096
    def opaque_reader(self, off: int) -> int: ...

    #@ requires 0 <= off and off < 64
    def _read_key(self, off: int) -> int:
        return self.disk[off]
