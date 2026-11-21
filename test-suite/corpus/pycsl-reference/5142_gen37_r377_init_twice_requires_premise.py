r"""Test 5142 -- gen #37 route #377 (expected FAIL): a dead first `__init__`'s `#@ requires x >= 0` became the constructor-goal premise (CPython `C(-3).x` is -3). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
#@ class invariant self.x >= 0
class C:
    #@ requires x >= 0
    def __init__(self, x: int) -> None:
        self.x = x

    def __init__(self, x: int) -> None:
        self.x = x

#@ ensures \result >= 0
def f(c: C) -> int:
    return c.x

if __name__ == "__main__":
    print(f(C(-3)))
