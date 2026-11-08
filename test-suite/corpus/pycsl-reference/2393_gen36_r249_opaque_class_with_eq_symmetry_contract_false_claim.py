r"""Test 2393 — route #249 (expected FAIL): a class the model does not carry as a record (no fields:
`type a = int`) that defines its own `__eq__`: `requires x == y` PROVED `ensures y == x` for `x: A`,
`y: A`. CPython: `A.__eq__` is `id(self) < id(o)`, so exactly one order holds.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
class A:
    def __eq__(self, o: object) -> bool:
        return id(self) < id(o)


#@ requires x == y
#@ ensures y == x
#@ assigns \nothing
def f(x: A, y: A) -> int:
    return 0


if __name__ == "__main__":
    a, b = A(), A()
    x, y = (a, b) if id(a) < id(b) else (b, a)
    assert x == y and not (y == x)
