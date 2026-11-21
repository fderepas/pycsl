r"""Test 3890 -- gen #37 route #307 (expected FAIL): `k.bump() - k.bump()` (two effectful method calls) was emitted as one application, evaluated right-to-left; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe g04_method_self_order).
"""
# pycsl-expected: FAIL
class K:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1 and \result == self.n
    def bump(self) -> int:
        self.n = self.n + 1
        return self.n

#@ ensures \result == 1
def f() -> int:
    k = K()
    return k.bump() - k.bump()

if __name__ == "__main__":
    assert f() == 1
