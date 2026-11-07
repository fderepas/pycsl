r"""Test 2223 — ch15 seam (expected FAIL): the element of `for line in r.lines` is a real string
whose length is not always 0. CPython: `total_len(Report(["ab"]))` is 2, so `\result == 0`
must stay unproved. Control: 2222.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class Report:
    lines: List[str] = field(default_factory=list)


#@ ensures \result == 0
#@ assigns \nothing
def total_len(r: Report) -> int:
    n = 0
    #@ loop invariant n >= 0
    for line in r.lines:
        n = n + len(line)
    return n


if __name__ == "__main__":
    assert total_len(Report(["ab"])) == 2
