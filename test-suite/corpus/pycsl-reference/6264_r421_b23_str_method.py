r"""Test 6264 -- route #421 (expected FAIL): red team 33 witness `b23_str_method` (getting-better/open-routes/witnesses-r421/b23_str_method.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
K = 'a b'.split()


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
