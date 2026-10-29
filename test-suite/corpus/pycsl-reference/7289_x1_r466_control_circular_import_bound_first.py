r"""Test 7289 -- route #466 CONTROL (expected PASS: PROVED at base and candidate): a circular import whose name `g` is bound BEFORE the cycle closes (CPython's partial module already has it).
"""
# pycsl-expected: PASS
from multi_file_lib.x1_hc466b import g


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
