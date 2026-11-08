r"""Test 6278 -- route #421 (expected FAIL): red team 33 witness `h03_cb_chain` (getting-better/open-routes/witnesses-r421/h03_cb_chain.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class C:
    K = A = [1]


#@ no_exception \all
def f() -> int:
    s = {C.K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
