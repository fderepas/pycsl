r"""Test 4902 -- gen #37 route #364 (expected FAIL): `__hash__ = None if True else object.__hash__`; `{r}` PROVED (CPython TypeError). REFUSED now (route #364).
"""
# pycsl-expected: FAIL
class R:
    __hash__ = None if True else object.__hash__

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
