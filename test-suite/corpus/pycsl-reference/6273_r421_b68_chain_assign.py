r"""Test 6273 -- route #421 (expected FAIL): red team 33 witness `b68_chain_assign` (getting-better/open-routes/witnesses-r421/b68_chain_assign.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
K = A = [1]


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
