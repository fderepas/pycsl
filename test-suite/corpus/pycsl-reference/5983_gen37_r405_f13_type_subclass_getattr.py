r"""Test 5983 -- gen #37 route #405 (expected FAIL): red team 32 witness `f13_type_subclass_getattr` -- a class created at run time from a file class escapes the closed world (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R405-DYNAMIC-SUBCLASS).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    S = type("S", (R,), {"k": 5})
    try:
        r = f(S())
        if not (r == 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
