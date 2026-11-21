r"""Test 5052 -- gen #37 route #373 (expected FAIL): an UNANNOTATED nested def returning `self`; PROVED at base (CPython 1). REFUSED now.
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        def g():
            return self
        t = g()
        return t - t

if __name__ == "__main__":
    assert W().m() == 0, W().m()
