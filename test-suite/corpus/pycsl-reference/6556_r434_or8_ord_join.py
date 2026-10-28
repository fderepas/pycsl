r"""Test 6556 -- route #434 (expected FAIL): red team 34 witness `or8_ord_join` (getting-better/open-routes/witnesses-r434/or8_ord_join.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str) -> int:
    return ord("".join([s, s]))


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
