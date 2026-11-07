r"""Test 6312 -- route #427 (expected FAIL): red team 33 witness `m13_genexp_set` (getting-better/open-routes/witnesses-r427/m13_genexp_set.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: set) -> int:
    for x in (y for y in s):
        s.add(x + 100)
    return 0


if __name__ == "__main__":
    try:
        r = f({1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
