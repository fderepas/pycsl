r"""Test 6270 -- route #421 (expected FAIL): red team 33 witness `b55_staticmethod_call` (getting-better/open-routes/witnesses-r421/b55_staticmethod_call.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class C:
    @staticmethod
    def m() -> list:
        return [1]


K = C.m()


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
