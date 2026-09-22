r"""Test 1723 — ROUTE #212 CONTROL: `--verify-imports` accepts an HONEST dependency.

Identical to 1722 except the import is `multi_file_lib/r212_verified.py`, whose frame tells
the truth (`#@ assigns a[0]` / `#@ ensures a[0] == 5`). The flag verifies the dependency,
the dependency proves, and this file proves. If it ever fails, `--verify-imports` has become
a ban on imports rather than a certificate for them.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare --verify-imports
from typing import List

from multi_file_lib.r212_verified import touch

_ = 0  # anchor


#@ requires \length(a) >= 1
#@ ensures \result == 5
def caller(a: List[int]) -> int:
    touch(a)
    return a[0]
