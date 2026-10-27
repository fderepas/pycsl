r"""Test 6282 -- route #422 (expected FAIL): red team 33 witness `c27_str_split_unbound` (getting-better/open-routes/witnesses-r422/c27_str_split_unbound.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f() -> int:
    k = str.split('a b')
    s = {k}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
