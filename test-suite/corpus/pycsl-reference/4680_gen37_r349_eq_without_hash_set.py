r"""Test 4680 -- gen #37 route #349 (expected FAIL): (new) `__eq__` without `__hash__`, `{r}`; PROVED (CPython TypeError). REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x = 0
    def __eq__(self, o: object) -> bool:
        return True

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
