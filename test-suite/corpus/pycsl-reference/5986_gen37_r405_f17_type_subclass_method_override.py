r"""Test 5986 -- gen #37 route #405 (expected FAIL): red team 32 witness `f17_type_subclass_method_override` -- a class created at run time from a file class escapes the closed world (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R405-DYNAMIC-SUBCLASS).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.x: int = 1

    #@ ensures \result == 1
    def g(self) -> int:
        return 1


#@ ensures \result == 1
def f(b: B) -> int:
    return b.g()


if __name__ == "__main__":
    D = type("D", (B,), {"g": lambda s: 2})
    try:
        r = f(D())
        if not (r == 1):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
