r"""Test 6307 -- route #426 (expected FAIL): red team 33 witness `f12_int_pct_big` (getting-better/open-routes/witnesses-r426/f12_int_pct_big.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> str:
    return f"{n:%}"


if __name__ == "__main__":
    try:
        r = f(10**400)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
