r"""Test 6610 -- route #438 (expected FAIL): red team 34 y14: `{r.t}` of a field annotated `tuple`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self, t: tuple) -> None:
        self.t: tuple = t


#@ no_exception \all
def f(r: R) -> int:
    s = {r.t}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R(([1],)))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
