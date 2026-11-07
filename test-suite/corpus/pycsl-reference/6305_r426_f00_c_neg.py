r"""Test 6305 -- route #426 (expected FAIL): red team 33 witness `f00_c_neg` (getting-better/open-routes/witnesses-r426/f00_c_neg.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> str:
    return f"{n:c}"


if __name__ == "__main__":
    try:
        r = f(-1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
