r"""Test 6315 -- route #427 (expected FAIL): red team 33 witness `w12_genexp_nested_gen` (getting-better/open-routes/witnesses-r427/w12_genexp_nested_gen.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(d: dict) -> int:
    for k in (x for x in (y for y in d)):
        d[k + 100] = 0
    return 0


if __name__ == "__main__":
    try:
        r = f({1: 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
