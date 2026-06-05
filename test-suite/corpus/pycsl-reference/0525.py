"""Test 0525 — faithful KeyError dict read has teeth: an unproven key FAILS.

Negative companion to 0524. Under `#@ no_exception KeyError`, `d[k]` on a key not
provably present cannot discharge the `has_key` obligation (`Map.get d k <>
None`) — that undischarged obligation IS the KeyError. So the function does not
verify (`# pycsl-expected: FAIL`), confirming the faithful model *rejects* an
unchecked dict read rather than optimistically returning a default. (Without
`#@ no_exception KeyError`, the read would be the ambient optimistic read and
this would pass — the faithful semantics is the opt-in.)
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
#@ no_exception KeyError
def unsafe_read(d: Dict[int, int], k: int) -> int:
    return d[k]
