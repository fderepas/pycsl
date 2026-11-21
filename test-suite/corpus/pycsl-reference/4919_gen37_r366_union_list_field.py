r"""Test 4919 -- gen #37 route #366 (expected FAIL): frozen dataclass field `Union[int, List[int]]`; `{d}` (CPython TypeError). REFUSED now (route #366: every Union argument).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Union

@dataclass(frozen=True)
class D:
    v: Union[int, List[int]]

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D([1])))
