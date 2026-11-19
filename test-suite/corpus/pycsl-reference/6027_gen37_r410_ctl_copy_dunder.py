r"""Test 6027 -- gen #37 route #410 (expected PASS): CONTROL: `copy.copy` of a frozen dataclass without copy-protocol methods hashed (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import copy
from dataclasses import dataclass


@dataclass(frozen=True)
class D:
    x: int


#@ no_exception \all
#@ ensures \result == 1
def f(d: D) -> int:
    s = {copy.copy(d)}
    return 1


if __name__ == "__main__":
    print(f(D(1)))
