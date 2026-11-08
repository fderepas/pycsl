r"""Test 5440 -- gen #37 systematic rule GD / route #389 (expected FAIL): red team 30 `g12_getattr_mangled_name` -- `getattr(o, name, 0)` folded to the default although CPython finds the attribute; PROVED at base 7bf752d4e (CPython: VIOLATION f = 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: the lookup is not fully modelled).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.__k: int = 5


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "_R__k", 0)


if __name__ == "__main__":
    v = f(R())
    print("VIOLATION f =", v) if v != 0 else print("no violation")
