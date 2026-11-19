r"""Test 6271 -- route #421 (expected FAIL): red team 33 witness `b56_func_result` (getting-better/open-routes/witnesses-r421/b56_func_result.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
def mk() -> list:
    return [1]


K = mk()


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
