r"""Test 6279 -- route #421 (expected FAIL): red team 33 witness `h07_cb_via_self` (getting-better/open-routes/witnesses-r421/h07_cb_via_self.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class C:
    K = bytearray(1)

    #@ no_exception \all
    def g(self) -> int:
        s = {self.K}
        return len(s)


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
