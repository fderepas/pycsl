r"""Test 2222 — ch15 seam: `for x in r.<f>` over a RECORD PARAM's `List[str]` field (emitted
`array string`) iterates the REAL array — bound `Array.length r.lines`, element
`r.lines[!idx]` (a real `string`), and the loop target is a string local. At base it fell to
the opaque `iter_length`/`iter_get : int -> int` applied to an `array string` (L3-tc type
error: refused). Contract: the summed length of the lines is non-negative and the membership
flag is 0/1. CPython: `total_len(Report(["ab", "c"]))` is 3, `has_x(Report(["a", "x"]))` is 1.
Expected PASS. False-claim twins: 2223, 2224.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Report:
    lines: List[str] = field(default_factory=list)


#@ ensures \result >= 0
#@ assigns \nothing
def total_len(r: Report) -> int:
    n = 0
    #@ loop invariant n >= 0
    for line in r.lines:
        n = n + len(line)
    return n


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def has_x(r: Report) -> int:
    for line in r.lines:
        if line == "x":
            return 1
    return 0


if __name__ == "__main__":
    assert total_len(Report(["ab", "c"])) == 3
    assert has_x(Report(["a", "x"])) == 1
    assert has_x(Report(["a"])) == 0
