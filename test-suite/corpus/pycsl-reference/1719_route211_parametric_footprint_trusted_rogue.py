r"""Test 1719 — ROUTE #211: route #210's hole in the PARAMETRIC (`footprint`) form, where
the twin is one annotation line away.

0614's design: `#@ happy inode_conf(n): protects d.disk[512 + n*64 : 512 + (n+1)*64]`
parameterises a per-object region; a method binds it with `#@ footprint inode_conf(k)`, and
a NON-exempt method with NO footprint that writes the path gets `#@ check False` — forbidden
outright. That stamp is inert in a body that is never lowered.

MEASURED: `rogue`, `#@ \trusted`, no footprint, not exempt, writing `d.disk[900]` — inside
object 6's region — printed "Verification SUCCESS! All contracts formally proven". The SAME
function with the `#@ \trusted` line removed FAILS. One annotation line flips a demonstrated
containment violation into a green run.

Controls: 0614 PROVES, 0615 stays FAIL, 1253 (route #92's footprinted point write) PROVES,
1047 stays refused.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
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


#@ requires v >= 0
#@ assigns d.disk
#@ \trusted
def rogue(v: int) -> None:
    d.disk[900] = v
