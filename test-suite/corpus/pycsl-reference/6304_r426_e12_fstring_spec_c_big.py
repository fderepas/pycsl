r"""Test 6304 -- route #426 (expected FAIL): red team 33 witness `e12_fstring_spec_c_big` (getting-better/open-routes/witnesses-r426/e12_fstring_spec_c_big.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> str:
    return f"{n:c}"


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
