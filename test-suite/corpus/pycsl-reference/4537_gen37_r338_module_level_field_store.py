r"""Test 4537 -- gen #37 route #338 (expected FAIL): a MODULE-LEVEL store `K.r = 0.5` on an instance: PROVED before (CPython False for `g(K)`). REFUSED now.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 0

#@ ensures \result == True
def g(c: C) -> bool:
    return c.r % 1 == 0

K = C()
K.r = 0.5

if __name__ == "__main__":
    assert g(K) == True
