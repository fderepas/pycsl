r"""Test 6309 -- route #426 (expected FAIL): red team 33 witness `m05_fspec_dot2f` (getting-better/open-routes/witnesses-r426/m05_fspec_dot2f.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> str:
    return f"{n:.2f}"


if __name__ == "__main__":
    try:
        r = f(10**400)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
