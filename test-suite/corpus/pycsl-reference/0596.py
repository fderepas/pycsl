"""Test 0596 — negative: a false fact about a global array-field read is unprovable (0442.md B1).

Same concrete read/write of `d.disk[i]` as `0595`, but the postcondition over-claims
`\result == 1` while the two reads of the just-written element are equal, so the difference is
`0`. The VC refutes `== 1`, confirming the field reads are concrete and consistent (not a free
abstract `subscript_get` whose two applications could differ).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare

#@ class invariant \length(self.disk) >= 8
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0, 0, 0, 0, 0, 0, 0, 0]


d = Disk()


#@ requires 0 <= i and i < 8
#@ ensures \result == 1
#@ assigns d.disk
def poke(i: int, v: int) -> int:
    d.disk[i] = v
    x = d.disk[i]
    y = d.disk[i]
    return y - x
