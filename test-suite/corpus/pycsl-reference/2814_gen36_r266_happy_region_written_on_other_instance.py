r"""Test 2814 — route #266 (expected FAIL): a non-exempt method writes ANOTHER instance's
region, `o.disk[600] = 9`. CPython: t.disk[600] = 9. Now refused.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ class invariant \length(self.disk) >= 4096
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_meta

class Store:
    def __init__(self) -> None:
        self.disk: list[int] = [0] * 4096

    #@ requires 0 <= off and off < 4096
    #@ assigns self.disk
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v

    #@ assigns o.disk
    def evil(self, o: "Store") -> None:
        o.disk[600] = 9

if __name__ == "__main__":
    s = Store(); t = Store(); s.evil(t); print("t.disk[600] =", t.disk[600])
