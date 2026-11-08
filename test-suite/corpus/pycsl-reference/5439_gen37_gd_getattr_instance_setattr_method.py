r"""Test 5439 -- gen #37 systematic rule GD / route #389 (expected FAIL): red team 30 `g09_getattr_instance_setattr_method` -- `getattr(o, name, 0)` folded to the default although CPython finds the attribute; PROVED at base 7bf752d4e (CPython: VIOLATION f = 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: the lookup is not fully modelled).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1
        setattr(self, "k", 5)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    r = f(R())
    print("VIOLATION f =", r) if r != 0 else print("no violation")
