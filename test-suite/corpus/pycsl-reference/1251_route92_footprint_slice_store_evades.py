"""Test 1251 — route #92, NEGATIVE: a SLICE store may not evade per-object confinement.

The second carrier of route #92, and the one that proves the first was not an isolated slip:
`_collect_protect_index_sites` skips a `Slice` subscript exactly as it skips an `Attribute`
target, and the same absent "non-footprint reject" was supposed to catch it. The docstring
named BOTH cases and neither was caught.

MEASURED BEFORE THE REPAIR: this file VERIFIED, and — the point that makes it a real carrier
rather than an erasure artefact — `requires d.disk[512] == 7` with `ensures d.disk[512] == 7`
REFUSED. So the slice store is NOT erased by the value model: the write genuinely lands inside
object 0's protected region [512, 576) while the property asserting per-object containment is
being proved.

Both carriers were measured BEFORE either was repaired, per the route #86 lesson that fixing
one carrier is the instrument that reveals the other — two independent evasions that produce
the same "it verifies" are indistinguishable until one is closed.
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

def sl(a: list) -> None:

    d.disk[512:576] = a  # slice store across object 0's whole region, unchecked
