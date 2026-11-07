r"""Test 4678 -- gen #37 route #349 (expected FAIL): witness e08: explicit `__hash__ = None`, `{r}`; PROVED (CPython TypeError). REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
from typing import Dict
class R:
    def __init__(self) -> None:
        self.x = 0
    __hash__ = None  # type: ignore

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    d: Dict[int, int] = {}
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
