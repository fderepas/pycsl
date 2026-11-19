r"""Test 4576 -- gen #37 route #342: CONTROL: witness 4571 with the `__class__` store replaced by constructing the target class (`d = C()`), the PYCSL-R342-CLASS-REASSIGNMENT advice followed; `c.r % 1 == 0` PROVES (CPython True).
"""
class C:
    def __init__(self) -> None:
        self.r = 1

class D:
    def __init__(self) -> None:
        self.r = 0.5

#@ ensures \result == True
def f(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    c = C()
    d = C()
    assert f(d) == True
