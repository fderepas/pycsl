r"""Test 4519 -- gen #37 route #336 (expected FAIL): store into a `Sequence[int]` parameter (a tuple at run time) under `no_exception \all`; CPython TypeError. REFUSED (PYCSL-R336-READONLY-VIEW-STORE).
"""
# pycsl-expected: FAIL
from typing import Tuple, Sequence, Mapping
from types import MappingProxyType
#@ requires len(xs) > 0
#@ no_exception \all
def f(xs: Sequence[int]) -> None:
    xs[0] = 1
if __name__ == "__main__":
    f((0,))
