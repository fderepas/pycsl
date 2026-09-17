r"""Test 1565 - ROUTE #165 (gen #29): a PARAM-referencing ensures (`\result >= k`) on the receiver-less stub; `c.x = -5; c.get(3) >= 3` PROVED at HEAD; CPython -2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= k
    def get(self, k: int) -> int:
        return self.x + k


#@ ensures \result >= 3
def probe() -> int:
    c = C()
    c.x = -5
    return c.get(3)

