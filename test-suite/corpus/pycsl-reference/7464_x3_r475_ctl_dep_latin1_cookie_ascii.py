r"""Test 7464 -- route #475 (control, expected PASS): control -- a `latin-1` cookie over ASCII-only text decodes identically, so the dependency keeps verifying (`n // K` with `K = 3`).
"""
# pycsl-expected: PASS
from multi_file_lib.x3_h475e import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
