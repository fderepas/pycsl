r"""Test 1964 — gen #36 (expected PASS): a `-> List[str]` function with an EARLY return
carries every return through the `Return_seq_str` (`seq string`) carrier. A return of a
split comprehension (`[p.strip() for p in line.split(",")]`, lowered to an `array string`)
was bridged with the monomorphic `snapshot : array int -> seq int` and failed L3-tc. It now
uses the string twin `snapshot_str` (length- and element-preserving), and the empty-input
path proves `len(\result) == 0` -- `len(\result)` of an `array string` result is now
`Array.length result` (was the opaque `iter_length`). Twin: 1965 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List


#@ ensures len(line) == 0 ==> len(\result) == 0
def names(line: str) -> List[str]:
    if not line:
        return []
    return [p.strip() for p in line.split(",")]
