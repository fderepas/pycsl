r"""Test 6624 -- route #439 (expected FAIL): red team 34 s0: `setattr(self, nm, [1])` in `__init__` (a computed name), then `{r.x}` with `x: int`; `f(R("x"))`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self, nm: str) -> None:
        self.x: int = 1
        setattr(self, nm, [1])


#@ no_exception \all
def f(r: R) -> int:
    s = {r.x}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R("x"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
