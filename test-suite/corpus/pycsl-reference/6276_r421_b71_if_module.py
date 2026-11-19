r"""Test 6276 -- route #421 (expected FAIL): red team 33 witness `b71_if_module` (getting-better/open-routes/witnesses-r421/b71_if_module.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import sys
if sys.argv:
    K = [1]
else:
    K = 1


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
