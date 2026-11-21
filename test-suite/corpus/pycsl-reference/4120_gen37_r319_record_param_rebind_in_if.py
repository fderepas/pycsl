r"""Test 4120 -- gen #37 route #319 (expected FAIL): a RECORD parameter rebound inside an `if` (`o = C(2)`) was a block-scoped `let`; the later `o.n = 5` wrote the CALLER object, so `ensures o.n == 5` PROVED (CPython: caller untouched when b). REFUSED.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self, n: int) -> None:
        self.n = n

#@ ensures o.n == 5
def f(o: C, b: bool) -> None:
    if b:
        o = C(2)
    o.n = 5

if __name__ == "__main__":
    a = C(1)
    f(a, True)
    assert a.n == 5, a.n
