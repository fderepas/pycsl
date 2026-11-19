r"""Test 4905 -- gen #37 route #364 (expected FAIL): `__eq__, tag = (lambda ..), 1` (tuple target); `{r}` PROVED (CPython TypeError). REFUSED now (route #364).
"""
# pycsl-expected: FAIL
class R:
    __eq__, tag = (lambda self, o: True), 1

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
