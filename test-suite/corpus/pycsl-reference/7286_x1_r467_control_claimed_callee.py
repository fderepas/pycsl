r"""Test 7286 -- route #467 CONTROL (expected PASS: PROVED at base and candidate): the imported callee claims `no_exception \all` (its own body proves), so the caller's claim is covered.
"""
# pycsl-expected: PASS
from multi_file_lib.x1_hc467 import g


#@ no_exception \all
#@ requires n >= 0
#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
