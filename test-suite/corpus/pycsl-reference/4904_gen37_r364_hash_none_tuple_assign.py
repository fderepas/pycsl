r"""Test 4904 -- gen #37 route #364 (expected FAIL): `__hash__, tag = None, 1`; `{r}` PROVED (CPython TypeError). REFUSED now (route #364).
"""
# pycsl-expected: FAIL
class R:
    __hash__, tag = None, 1

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
