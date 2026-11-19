r"""Test 5433 -- gen #37 systematic rule S1 / route #381 (expected FAIL): red team 29 `h52_abc_mapping` -- `class D(Mapping)` (a standard-library base the model has no entry for) hashed under `no_exception`; PROVED at base 7bf752d4e (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE).
"""
# pycsl-expected: FAIL
from collections.abc import Mapping
from typing import Iterator

class D(Mapping):
    def __getitem__(self, k: int) -> int:
        return 0
    def __iter__(self) -> Iterator[int]:
        return iter([])
    def __len__(self) -> int:
        return 0

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
