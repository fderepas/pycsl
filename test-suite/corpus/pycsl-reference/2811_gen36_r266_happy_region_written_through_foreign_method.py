r"""Test 2811 — route #266 (expected FAIL): as 2810, but the writer is a METHOD of another class,
`h.poke(self.disk, 600)`. CPython: disk[600] = 9. Now refused (the field escapes as a call argument).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
class Helper:
    def __init__(self) -> None:
        self.k: int = 0

    #@ requires 0 <= i and i < len(a)
    #@ assigns a[i]
    def poke(self, a: list[int], i: int) -> None:
        a[i] = 9

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
    def evil(self, h: Helper) -> None:
        h.poke(self.disk, 600)

if __name__ == "__main__":
    s = Store(); s.evil(Helper()); print("disk[600] =", s.disk[600])
