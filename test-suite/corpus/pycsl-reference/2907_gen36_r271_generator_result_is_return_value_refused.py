r"""Test 2907 — route #271 (expected FAIL, refused): `gen` contains `yield`, so `gen()` returns a
GENERATOR object; the `return 3` only sets `StopIteration.value`. The eager lowering proved
`gen`'s `\result == 3` and the caller's `return gen()` `\result == 3`. CPython: `f()` is a
generator, not 3. PROVED at c9d7f157.
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ assigns \nothing
def gen() -> int:
    yield 1
    return 3

#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return gen()

if __name__ == "__main__":
    print(f() == 3, type(f()).__name__)
