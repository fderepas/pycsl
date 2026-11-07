r"""Test 5039 -- gen #37 route #372 (expected FAIL): NEW shape: `for d in ds` with `ds: List[D]`, `{d}` (the loop element class from the iterable annotation) (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(ds: List[D]) -> int:
    for d in ds:
        s = {d}
    return 1

if __name__ == "__main__":
    print(g([D(1)]))
