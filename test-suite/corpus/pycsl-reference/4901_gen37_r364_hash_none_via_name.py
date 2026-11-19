r"""Test 4901 -- gen #37 route #364 (expected FAIL): `__hash__ = NOHASH` (a name bound to None); `{r}` PROVED (CPython TypeError). REFUSED now (route #364: a non-def `__hash__` binding may be None).
"""
# pycsl-expected: FAIL
NOHASH = None

class R:
    __hash__ = NOHASH

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
