r"""Test 2818 — route #266 (expected FAIL): `protects d.disk` is bypassed by a non-exempt method
OF THE DISK CLASS itself, which writes the same location under the spelling `self.disk[600]`
(called through `d.smash()` from non-exempt `evil`). CPython: 9. Now refused.
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

    #@ assigns self.disk
    def smash(self) -> None:
        self.disk[600] = 9

d = Disk()

#@ assigns d.disk
def evil() -> None:
    d.smash()

#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0

if __name__ == "__main__":
    evil(); print("d.disk[600] =", d.disk[600])
