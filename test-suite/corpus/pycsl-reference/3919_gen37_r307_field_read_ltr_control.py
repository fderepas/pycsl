r"""Test 3919 -- gen #37 route #307 (expected PASS): CONTROL: `k.n + k.bump()` proves the CPython value 0 (field read before the method write).
"""
# pycsl-expected: PASS
class K:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1 and \result == 0
    def bump(self) -> int:
        self.n = self.n + 1
        return 0

#@ ensures \result == 0
def f() -> int:
    k = K()
    return k.n + k.bump()

if __name__ == "__main__":
    assert f() == 0
