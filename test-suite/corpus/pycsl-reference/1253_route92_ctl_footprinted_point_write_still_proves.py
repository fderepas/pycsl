"""Test 1253 — route #92 CONTROL (non-vacuity): a footprinted point write still PROVES.

Clause (R3b) rejects whole-array and slice stores. It must not disturb the capability the
parametric form exists to provide: a method that declares `#@ footprint inode_conf(k)` and
writes inside object k's region must still verify. Here `writer2` writes the LAST index of its
own footprint, `512 + k*64 + 63`, and the injected containment check discharges.

This is the file that makes 1250's and 1251's refusals evidence rather than noise.
"""
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

#@ requires 0 <= k and k < 8

#@ footprint inode_conf(k)

#@ assigns d.disk

def writer2(k: int, v: int) -> None:

    d.disk[512 + k * 64 + 63] = v   # last index of object k's own region
