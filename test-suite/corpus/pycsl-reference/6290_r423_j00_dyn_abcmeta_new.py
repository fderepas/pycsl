r"""Test 6290 -- route #423 (expected FAIL): red team 33 witness `j00_dyn_abcmeta_new` (getting-better/open-routes/witnesses-r423/j00_dyn_abcmeta_new.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    import abc
    D = abc.ABCMeta.__new__(abc.ABCMeta, "D", (B,), {"__hash__": None})
    try:
        r = f(D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
