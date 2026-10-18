r"""Test 2908 — route #271 (expected FAIL, refused): a `yield` makes `__init__` a generator
function, so CPython's `C()` raises `TypeError: __init__() should return None, not
'generator'`. The eager lowering ran the body at construction and proved `\result == 5`.
PROVED at c9d7f157.
"""
# pycsl-expected: FAIL
class C:
    #@ assigns self.n
    def __init__(self) -> None:
        self.n: int = 5
        yield 0

#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.n

if __name__ == "__main__":
    try:
        print(f())
    except TypeError as exc:
        print("TypeError:", exc)
