r"""Test 4578 -- gen #37 route #342 (expected FAIL): NEW latent shape (p7, r341 executor): own `__init__` `self.x = 5; self.helper()` (a `self.m()` call makes route #150 widen every field to unknown, so NO goal is emitted): PROVED `x == 0` (CPython 5). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 5
        self.helper()

    def helper(self) -> None:
        pass

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
