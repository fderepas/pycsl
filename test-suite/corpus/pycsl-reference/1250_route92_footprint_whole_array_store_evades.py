"""Test 1250 — route #92, NEGATIVE: a WHOLE-ARRAY store may not evade per-object confinement.

`happy inode_conf(n): protects d.disk[512 + n*64 : 512 + (n+1)*64]` is the PARAMETRIC (R3)
confinement form: a method binds one object's region with `#@ footprint inode_conf(k)`, and
each point write must prove containment in that object's slice. A non-exempt method with NO
footprint that writes the path is supposed to be forbidden outright (`check False`).

It was not. `_collect_protect_index_sites` returns only POINT writes, and the `check False`
"non-footprint reject" fires only on the sites that collector returns — so a WHOLE-ARRAY store
`d.disk = a` was in no list and got no check. Its own docstring had deferred exactly this case
to that reject: *"Slice/whole-array writes to a parametric path are not certifiable
per-object; they are left to the non-footprint reject."* There was no such reject.

MEASURED BEFORE THE REPAIR: this file VERIFIED; with `requires a[512] == 99` the claim
`ensures d.disk[512] == 99` PROVED (index 512 is inside object 0's region [512, 576)); and the
preservation claim `ensures d.disk[512] == 7` REFUSED. Controls: a non-exempt footprint-less
POINT write refused, and 0614's footprinted `writer` proved — so the branch was live.

A DEFERRAL IS A CLAIM ABOUT ANOTHER PIECE OF CODE, AND IT IS THE ONE KIND OF CLAIM NOBODY
RE-READS. Repaired sound-by-rejection by clause (R3b).
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


#@ requires 0 <= k and k < 8
#@ footprint inode_conf(k)
#@ assigns d.disk
def writer(k: int, v: int) -> None:
    d.disk[512 + k * 64] = v


#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0

#@ requires \length(a) >= 1024

#@ assigns d.disk

def wipe(a: list) -> None:

    d.disk = a          # whole-array store: replaces EVERY object's region, unchecked
