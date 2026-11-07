r"""Test 6268 -- route #421 (expected FAIL): red team 33 witness `b52_copy_copy_list` (getting-better/open-routes/witnesses-r421/b52_copy_copy_list.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import copy
A = [1]
K = copy.copy(A)


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
