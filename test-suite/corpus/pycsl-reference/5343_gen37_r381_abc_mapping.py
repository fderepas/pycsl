r"""Test 5343 -- gen #37 route #381 (expected FAIL): `class D(collections.abc.Mapping)`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
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
