r"""Test 2820 — route #266 CONTROL (expected PASS): the EXEMPT owner may still hand self.disk to
a helper (it writes under the owner's authority), and a non-exempt method may still read
self.disk[i] and write OUTSIDE the region directly. CPython: 7 and 3.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires 0 <= i and i < len(a)
#@ assigns a[i]
def poke(a: list[int], i: int) -> None:
    a[i] = 7

_z = 0
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
    def _write_meta(self, off: int) -> None:
        poke(self.disk, off)

    #@ assigns self.disk
    def tidy(self) -> int:
        self.disk[3000] = 3
        return self.disk[3000]

if __name__ == "__main__":
    s = Store(); s._write_meta(600); print(s.disk[600], s.tidy())
