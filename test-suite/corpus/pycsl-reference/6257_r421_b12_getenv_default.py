r"""Test 6257 -- route #421 (expected FAIL): red team 33 witness `b12_getenv_default` (getting-better/open-routes/witnesses-r421/b12_getenv_default.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import os
K = os.getenv('PYCSL_NOPE_XYZ', [1])


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
