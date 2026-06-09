"""Test 0687 — negative: HAPPY exempt name is not a method (typo).

A bogus name in the `except` set (`nosuchmethod`) is rejected at semantic analysis — a
typo there would silently widen the property's coverage. Migrated to
core_ir_semantic._check_happy (module-level, via the front-end-plumbed `happy` blob,
which carries the SHORT method names the IR otherwise flattens to Class__method).
Characterization test for the IR migration (Phase B / AST-only, the last of the 5).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ class invariant \length(self.disk) >= 4096
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except nosuchmethod
class Store:
    def __init__(self) -> None:
        self.disk: list = bytearray(4096)

    #@ requires 0 <= off and off < 4096
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v
