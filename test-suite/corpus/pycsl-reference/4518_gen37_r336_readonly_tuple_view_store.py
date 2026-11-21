r"""Test 4518 -- gen #37 route #336 (expected FAIL): store into a `tuple[float, ...]` parameter read as `List[float]` would prove `no_exception \all`; CPython TypeError. REFUSED (PYCSL-R336-READONLY-VIEW-STORE).
"""
# pycsl-expected: FAIL
from typing import Tuple, Sequence, Mapping
from types import MappingProxyType
#@ requires len(xs) > 0
#@ no_exception \all
def f(xs: tuple[float, ...]) -> None:
    xs[0] = 1
if __name__ == "__main__":
    f((0,))
