r"""Test 6310 -- route #427 (expected FAIL): red team 33 witness `g07_genexp_dict` (getting-better/open-routes/witnesses-r427/g07_genexp_dict.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(d: dict) -> int:
    for k in (x for x in d):
        d[k + 100] = 0
    return 0


if __name__ == "__main__":
    try:
        r = f({1: 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
