r"""Test 5077 -- gen #37 route #376 (expected FAIL): `getattr(self, "k", 0)` on a record receiver with class attribute `k = -1`; PROVED at base (CPython -1). REFUSED now.
"""
# pycsl-expected: FAIL
class R:
    k = -1
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def m(self) -> int:
        return getattr(self, "k", 0)

if __name__ == "__main__":
    assert R().m() >= 0, R().m()
