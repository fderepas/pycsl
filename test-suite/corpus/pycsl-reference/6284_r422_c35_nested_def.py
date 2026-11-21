r"""Test 6284 -- route #422 (expected FAIL): red team 33 witness `c35_nested_def` (getting-better/open-routes/witnesses-r422/c35_nested_def.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f() -> int:
    def g() -> list:
        return [1]
    k = g()
    s = {k}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
