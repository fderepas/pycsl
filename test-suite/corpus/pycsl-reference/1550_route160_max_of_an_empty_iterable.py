r"""Test 1550 - ROUTE #160 (gen #29): `max([])` under `no_exception ValueError` PROVED; CPython raises. Refused unless the single iterable is a non-empty literal or `default=` is given.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    return max([])

