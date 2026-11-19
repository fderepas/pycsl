r"""Test 4963 -- gen #37 route #226: CONTROL for 4953: one parameter `a` (named like no field) stored into BOTH fields, `self.x = a; self.y = a`, under `#@ class invariant self.x == self.y`; the goal `forall x y a. x = a -> y = a -> (x = y)` is stated (no clash) and the file PROVES (CPython 0).
"""
#@ class invariant self.x == self.y
class D:
    def __init__(self, a: int) -> None:
        self.x = a
        self.y = a

#@ ensures \result == 0
def f(d: D) -> int:
    return d.x - d.y

if __name__ == "__main__":
    assert f(D(4)) == 0
