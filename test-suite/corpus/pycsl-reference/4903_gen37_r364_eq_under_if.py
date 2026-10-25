r"""Test 4903 -- gen #37 route #364 (expected FAIL): `def __eq__` nested under `if True:` in the class body; `{r}` PROVED (CPython TypeError). REFUSED now (route #364: any class-scope binding defines `__eq__`).
"""
# pycsl-expected: FAIL
class R:
    if True:
        def __eq__(self, o: object) -> bool:
            return True

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
