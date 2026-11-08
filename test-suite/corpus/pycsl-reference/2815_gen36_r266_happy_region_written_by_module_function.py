r"""Test 2815 — route #266 (expected FAIL): a non-exempt MODULE function writes `s.disk[600]`
directly. CPython: disk[600] = 9. Now refused.
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


#@ assigns s.disk
def attack(s: Store) -> None:
    s.disk[600] = 9

if __name__ == "__main__":
    s = Store(); attack(s); print("disk[600] =", s.disk[600])
