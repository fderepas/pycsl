r"""Test 6289 -- route #423 (expected FAIL): red team 33 witness `a34_dyn_getattr_alias` (getting-better/open-routes/witnesses-r423/a34_dyn_getattr_alias.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    T = type
    S = T("S", (R,), {"k": 5})
    try:
        r = f(S())
        if not (r == 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
