r"""Test 2384 — route #249 (expected FAIL): Same as 2370 with parameters declared `object`: `requires x == y` PROVED `ensures y == x`.
CPython `A()`, `B()`.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
#@ requires x == y
#@ ensures y == x
#@ assigns \nothing
def f(x: object, y: object) -> int:
    return 0


if __name__ == "__main__":
    class A:
        def __eq__(self, o: object) -> bool:
            return True

        def __hash__(self) -> int:
            return 0

    class B:
        def __eq__(self, o: object) -> bool:
            return False

        def __hash__(self) -> int:
            return 0

    x, y = A(), B()
    assert x == y and not (y == x)
