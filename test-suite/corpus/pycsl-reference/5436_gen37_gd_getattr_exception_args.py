r"""Test 5436 -- gen #37 systematic rule GD / route #388 (expected FAIL): red team 30 `g01_getattr_exception_args` -- `getattr(o, name, 0)` folded to the default although CPython finds the attribute; PROVED at base 7bf752d4e (CPython: VIOLATION f = ()). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: the lookup is not fully modelled).
"""
# pycsl-expected: FAIL
class E(Exception):
    def __init__(self) -> None:
        self.x: int = 1


#@ ensures \result == 0
def f(e: E) -> int:
    return getattr(e, "args", 0)


if __name__ == "__main__":
    r = f(E())
    print("VIOLATION f =", r) if r != 0 else print("no violation")
