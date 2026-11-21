r"""Test 4953 -- gen #37 route #226 (expected FAIL): `__init__(self, x: int, y: int)` stores `self.x = y; self.y = x` under `#@ class invariant self.x == self.y`. Increment 2 quantified field labels and parameters TOGETHER, so the goal read `forall x y. x = y -> y = x -> (x = y)` and PROVED `ensures \result == 0` on `d.x - d.y` (CPython `D(1, 2)` gives 1). REFUSED: PYCSL-R226-INIT-PARAM-FIELD-NAME-CLASH.
"""
# pycsl-expected: FAIL
#@ class invariant self.x == self.y
class D:
    def __init__(self, x: int, y: int) -> None:
        self.x = y
        self.y = x

#@ ensures \result == 0
def f(d: D) -> int:
    return d.x - d.y

if __name__ == "__main__":
    assert f(D(1, 2)) == 1
