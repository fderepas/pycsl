r"""Test 6311 -- route #427 (expected FAIL): red team 33 witness `m10_genexp_keys` (getting-better/open-routes/witnesses-r427/m10_genexp_keys.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(d: dict) -> int:
    for k in (x for x in d.keys()):
        d[k + 100] = 0
    return 0


if __name__ == "__main__":
    try:
        r = f({1: 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
