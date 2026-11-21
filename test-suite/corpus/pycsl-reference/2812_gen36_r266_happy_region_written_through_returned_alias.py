r"""Test 2812 — route #266 (expected FAIL): a non-exempt getter RETURNS self.disk and the
non-exempt caller writes `d[600] = 9` through the returned reference — no `self.disk[i]` site
exists. CPython: disk[600] = 9. Now refused (the field escapes by `return`).
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

    #@ ensures \result == self.disk
    def get(self) -> list[int]:
        return self.disk

    #@ assigns self.disk
    def evil(self) -> None:
        d = self.get()
        d[600] = 9

if __name__ == "__main__":
    s = Store(); s.evil(); print("disk[600] =", s.disk[600])
