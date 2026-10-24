r"""Test 4579 -- gen #37 route #342 (expected FAIL): NEW latent shape (p8, r341 executor): `b = B(); b.x = 5` in unverified `__main__` code under invariant `x == 0`: PROVED (CPython 5). REFUSED (PYCSL-R342-EXTERNAL-INVARIANT-STORE, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    b = B()
    b.x = 5
    assert f(b) == 0
