r"""Test 4520 -- gen #37 route #336 (expected FAIL): store into a `Mapping[str, int]` parameter (a MappingProxyType at run time) under `no_exception \all`; CPython TypeError. REFUSED (PYCSL-R336-READONLY-VIEW-STORE).
"""
# pycsl-expected: FAIL
from typing import Tuple, Sequence, Mapping
from types import MappingProxyType

#@ no_exception \all
def f(d: Mapping[str, int]) -> None:
    d["a"] = 1
if __name__ == "__main__":
    f(MappingProxyType({"a": 0}))
