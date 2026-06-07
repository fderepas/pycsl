"""Test 0615 — negative: a write outside the footprint region is caught (07-1143 R3).

Same parametric HAPPY as 0614, but `writer` writes `d.disk[512 + (k+1)*64]` — the FIRST index
of the NEXT object's region, outside its own footprint `inode_conf(k)`. The injected per-site
containment check is unprovable, surfacing the cross-object write as a violation.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare

#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
#@     except formatter

#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ requires 0 <= k and k < 7
#@ footprint inode_conf(k)
#@ assigns d.disk
def writer(k: int, v: int) -> None:
    d.disk[512 + (k + 1) * 64] = v


#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0
