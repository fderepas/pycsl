r"""Test 2810 — route #266 (expected FAIL): the HAPPY region-integrity policy (no non-exempt
method writes self.disk inside [512, 2560)) was PROVED of a class whose non-exempt `evil` passes
self.disk to a module helper `poke(a, i)` that writes `a[i] = 9` — a list is passed by reference,
and the per-site check keyed only on the spelling `self.disk[i]`. CPython: disk[600] = 9 (inside the
region). Now refused: the protected field may not escape a non-exempt method as a reference.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires 0 <= i and i < len(a)
#@ assigns a[i]
def poke(a: list[int], i: int) -> None:
    a[i] = 9

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
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v

    #@ assigns self.disk
    def evil(self) -> None:
        poke(self.disk, 600)

if __name__ == "__main__":
    s = Store(); s.evil(); print("disk[600] =", s.disk[600])
