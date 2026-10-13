r"""Test 1956 — gen #36 (expected PASS): W-IPM S-C4 — a list LOCAL initialised from a
string literal (`lines = ["[*] header:"]`) and then appended strings and joined (the mirror
`ConcurrencyChecker.summary` shape) is a `seq string` whose literal element is the REAL
string `(Seq.cons "[*] header:" Seq.empty)` (a `seq string`). Before S-C4 the literal was
int-hashed (`Seq.cons 1795694705 Seq.empty`, a `seq int`) and the string `Seq.snoc` failed
L3-tc. Twin: 1957 (false length claim, must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
_ = 0  # anchor
from typing import List


#@ requires len(s) >= 0
#@ ensures \result == 2
def count_lines(s: str) -> int:
    lines = ["[*] header:"]
    lines.append("  " + s)
    out = "\n".join(lines)
    return len(lines)
