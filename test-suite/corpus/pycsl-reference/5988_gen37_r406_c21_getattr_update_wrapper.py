r"""Test 5988 -- gen #37 route #406 (expected FAIL): red team 32 witness `c21_getattr_update_wrapper` -- a call to a callee the model does not read stores an attribute on the receiver (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING / PYCSL-R349-UNHASHABLE-RECORD: the call census (`_dy406`) makes every class UNKNOWN for GD and field / class-attribute reads UNKNOWN when hashed).
"""
# pycsl-expected: FAIL
import functools


class S:
    def __init__(self) -> None:
        self.k: int = 5


class R:
    def __init__(self) -> None:
        self.x: int = 1
        functools.update_wrapper(self, S(), assigned=(), updated=("__dict__",))


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        r = f(R())
        if not (r == 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
