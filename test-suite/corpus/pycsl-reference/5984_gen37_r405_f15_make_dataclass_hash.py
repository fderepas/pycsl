r"""Test 5984 -- gen #37 route #405 (expected FAIL): red team 32 witness `f15_make_dataclass_hash` -- a class created at run time from a file class escapes the closed world (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R405-DYNAMIC-SUBCLASS).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    import dataclasses
    D = dataclasses.make_dataclass("D", [], bases=(B,))
    try:
        r = f(D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
