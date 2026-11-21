r"""Test 2816 — route #266 (expected FAIL): the `protects d.disk` ownership form, bypassed the
same way — non-exempt `evil` calls `poke(d.disk, 600)`. CPython: 9. Now refused.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy own:
#@     protects d.disk
#@     except formatter

#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list[int] = [0] * 1024


d = Disk()

#@ requires 0 <= i and i < len(a)
#@ assigns a[i]
def poke(a: list[int], i: int) -> None:
    a[i] = 9

#@ assigns d.disk
def evil() -> None:
    poke(d.disk, 600)

#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0

if __name__ == "__main__":
    evil(); print("d.disk[600] =", d.disk[600])
