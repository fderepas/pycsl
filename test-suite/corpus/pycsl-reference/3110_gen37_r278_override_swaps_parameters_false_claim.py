r"""Test 3110 — route #278 (expected FAIL, refused): `B.m(self, y, x)` overrides
`A.m(self, x, y)`; both contracts say `\result == x`. The refinement goal renders the base's
contract over the SUB's binders, so `x` meant the second argument on both sides and the goal
held — while `a.m(1, 7)` on a `B` returns 7. PROVED under the flag. Parameters the base
contract mentions must keep their position.
"""
# pycsl-expected: FAIL


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires x > 0
    #@ ensures \result == x
    #@ assigns \nothing
    def m(self, x: int, y: int) -> int:
        return x


class B(A):
    #@ requires x > 0
    #@ ensures \result == x
    #@ assigns \nothing
    def m(self, y: int, x: int) -> int:
        return x


#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m(1, 7)


if __name__ == "__main__":
    print(use(B()))
    assert use(B()) == 7
