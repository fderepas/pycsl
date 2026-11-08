r"""Test 5991 -- gen #37 route #406 (expected FAIL): red team 32 witness `f49_getattr_ns_init_module_fn` -- a call to a callee the model does not read stores an attribute on the receiver (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING / PYCSL-R349-UNHASHABLE-RECORD: the call census (`_dy406`) makes every class UNKNOWN for GD and field / class-attribute reads UNKNOWN when hashed).
"""
# pycsl-expected: FAIL
import argparse


class R:
    def __init__(self) -> None:
        self.x: int = 1


def init(r: R) -> None:
    argparse.Namespace.__init__(r, k=5)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    r = R()
    init(r)
    try:
        r = f(r)
        if not (r == 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
