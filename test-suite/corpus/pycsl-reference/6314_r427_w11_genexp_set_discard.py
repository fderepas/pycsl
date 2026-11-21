r"""Test 6314 -- route #427 (expected FAIL): red team 33 witness `w11_genexp_set_discard` (getting-better/open-routes/witnesses-r427/w11_genexp_set_discard.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: set) -> int:
    for x in (y for y in s):
        s.discard(x)
    return 0


if __name__ == "__main__":
    try:
        r = f({1, 2})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
