r"""Test 5995 -- gen #37 route #406 (expected FAIL): red team 32 witness `k04_getattr_ns_classattr_hash` -- a call to a callee the model does not read stores an attribute on the receiver (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING / PYCSL-R349-UNHASHABLE-RECORD: the call census (`_dy406`) makes every class UNKNOWN for GD and field / class-attribute reads UNKNOWN when hashed).
"""
# pycsl-expected: FAIL
import argparse


class R:
    def __init__(self) -> None:
        self.x: int = 1
        argparse.Namespace.__init__(self, x=[1])


#@ no_exception \all
def f(r: R) -> int:
    s = {r.x}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
