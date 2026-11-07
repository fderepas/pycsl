r"""Test 4900 -- gen #37 route #364 (expected FAIL): `__eq__ = lambda ..` (no `__hash__`) makes the class unhashable; `{r}` under `no_exception \all` PROVED (CPython TypeError). REFUSED now (PYCSL-R349-UNHASHABLE-RECORD, route #364).
"""
# pycsl-expected: FAIL
class R:
    __eq__ = lambda self, o: True

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
