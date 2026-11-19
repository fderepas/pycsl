r"""Test 2224 — ch15 seam (expected FAIL): `for line in r.lines` visits the real elements, so a
`"x"` line is found. CPython: `has_x(Report(["a", "x"]))` is 1, so `\result == 0` must stay
unproved. Control: 2222.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class Report:
    lines: List[str] = field(default_factory=list)


#@ ensures \result == 0
#@ assigns \nothing
def has_x(r: Report) -> int:
    for line in r.lines:
        if line == "x":
            return 1
    return 0


if __name__ == "__main__":
    assert has_x(Report(["a", "x"])) == 1
