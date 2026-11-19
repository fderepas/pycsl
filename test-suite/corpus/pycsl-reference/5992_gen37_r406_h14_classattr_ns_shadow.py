r"""Test 5992 -- gen #37 route #406 (expected FAIL): red team 32 witness `h14_classattr_ns_shadow` -- a call to a callee the model does not read stores an attribute on the receiver (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING / PYCSL-R349-UNHASHABLE-RECORD: the call census (`_dy406`) makes every class UNKNOWN for GD and field / class-attribute reads UNKNOWN when hashed).
"""
# pycsl-expected: FAIL
import argparse


class C:
    K = 1

    def __init__(self) -> None:
        self.x: int = 1
        argparse.Namespace.__init__(self, K=[1])


#@ no_exception \all
def f(c: C) -> int:
    s = {c.K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(C())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
