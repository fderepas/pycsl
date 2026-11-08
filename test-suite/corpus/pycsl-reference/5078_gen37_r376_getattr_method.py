r"""Test 5078 -- gen #37 route #376 (expected FAIL): `getattr(r, "k", 0)` where `k` is a METHOD: CPython returns the bound method (`v == 0` False); folded to 0, PROVED. REFUSED now.
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x = 1

    def k(self) -> int:
        return 1

#@ ensures \result == 0
def f(r: R) -> int:
    v = getattr(r, "k", 0)
    return 0 if v == 0 else 1

if __name__ == "__main__":
    assert f(R()) == 0, f(R())
