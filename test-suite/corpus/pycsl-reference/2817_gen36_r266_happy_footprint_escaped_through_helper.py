r"""Test 2817 — route #266 (expected FAIL): the PARAMETRIC (footprint) form — `writer(k)` may
write only object k's region of d.disk, yet `poke(d.disk, 900)` writes outside it (object 6's
region for k = 0). CPython: d.disk[900] = 9. Now refused.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
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

#@ requires 0 <= k and k < 8
#@ footprint inode_conf(k)
#@ assigns d.disk
def writer(k: int, v: int) -> None:
    poke(d.disk, 900)

#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0

if __name__ == "__main__":
    writer(0, 1); print("d.disk[900] =", d.disk[900])
