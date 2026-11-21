r"""Test 7681 -- route #484 CONTROL (expected PASS: PROVED at base and candidate): the PEER only CALLS `y2_h484g.g` at import (no store), so the callee's binding stands.
"""
# pycsl-expected: PASS
import multi_file_lib.y2_c484p
from multi_file_lib.y2_h484g import g


#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
