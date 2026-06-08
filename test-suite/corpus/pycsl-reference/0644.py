"""Test 0644 — a dynamic exec is a worst-case mutator under HAPPY confinement (07-1839 P5).

A constant exec is spliced away before Module4 (P5b), so any exec reaching the HAPPY validator is
DYNAMIC and may write anything — including the protected region. A non-exempt method containing one
therefore cannot be confined by a HAPPY property: it is rejected with a hard error (the same teeth as
a non-exempt `\trusted` mutator without `#@ \preserves`, test 0462). To use exec here one must add the
method to the property's `except` set (acknowledging it as a trusted writer).
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

    def _write_meta(self, i: int, v: int) -> None:
        self.disk[i] = v

    def run(self, code: str) -> None:
        exec(code)
