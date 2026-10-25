r"""Test 5076 -- gen #37 route #376 (expected FAIL): `getattr(self, "k", 0)` with `k = -1` inherited from base A; PROVED at base (CPython -1). REFUSED now.
"""
# pycsl-expected: FAIL
class A:
    k = -1

class W(A):
    #@ ensures \result >= 0
    def m(self) -> int:
        return getattr(self, "k", 0)

if __name__ == "__main__":
    assert W().m() >= 0, W().m()
