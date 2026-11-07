r"""Test 5441 -- gen #37 systematic rule GD / route #389 (expected FAIL): red team 30 `g21_setattr_computed_name_then_getattr` -- `getattr(o, name, 0)` folded to the default although CPython finds the attribute; PROVED at base 7bf752d4e (CPython: VIOLATION f = 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: the lookup is not fully modelled).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self, name: str) -> None:
        self.x: int = 1
        setattr(self, name, 5)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    v = f(R("k"))
    print("VIOLATION f =", v) if v != 0 else print("no violation")
