r"""Test 5464 -- gen #37 systematic rule GD (expected PASS): CONTROL: `getattr(r, "k", 0)` over `R(B)` where both classes are file classes (the whole MRO is modelled, `object` included), no dynamic attribute store outside `__main__` (the driver's `setattr` is not verified code): the default is the answer; PROVED (CPython 0).
"""
# pycsl-expected: PASS
class B:
    def __init__(self) -> None:
        self.y: int = 2

class R(B):
    def __init__(self) -> None:
        self.x: int = 1

#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)

if __name__ == "__main__":
    r = R()
    assert f(r) == 0
    setattr(r, "z", 1)
