r"""Test 1708 — ROUTE #204 CONTROL: the same module with a COMPLETE interface frame.

Identical to 1707 except `#@ interface assigns a[0]` lists the target the body writes, so
the interface no longer hides a write from importers. This file must keep PROVING: route
#204's refusal is about a frame that omits a definition target, not about `#@ interface
assigns` as such. If this file ever fails, the refusal has become a ban on the feature.
"""
# pycsl-expected: PASS
from typing import List

_ = 0  # anchor


#@ requires \length(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == 5
#@ interface assigns a[0]
#@ interface requires \length(a) >= 1
def bump_ok(a: List[int]) -> None:
    a[0] = 5
