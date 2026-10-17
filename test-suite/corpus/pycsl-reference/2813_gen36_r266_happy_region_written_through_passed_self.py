r"""Test 2813 — route #266 (expected FAIL): non-exempt `evil` passes `self` to a module helper
that writes `s.disk[600] = 9` — the write's receiver is `s`, not `self`, so no check was stamped.
CPython: disk[600] = 9. Now refused (a write to the protected field through another receiver).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ assigns s.disk
def poke2(s: "Store") -> None:
    s.disk[600] = 9

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

    #@ assigns self.disk
    def evil(self) -> None:
        poke2(self)

if __name__ == "__main__":
    s = Store(); s.evil(); print("disk[600] =", s.disk[600])
