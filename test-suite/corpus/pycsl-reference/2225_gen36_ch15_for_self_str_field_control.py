r"""Test 2225 — ch15 seam, `self` receiver: `for line in self.lines` inside a method of the
record iterates the real `array string` field (the element is a string local). CPython:
`Report(["ab", "c"]).total_len()` is 3. Expected PASS.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Report:
    lines: List[str] = field(default_factory=list)

    #@ ensures \result >= 0
    #@ assigns \nothing
    def total_len(self) -> int:
        n = 0
        #@ loop invariant n >= 0
        for line in self.lines:
            n = n + len(line)
        return n


if __name__ == "__main__":
    assert Report(["ab", "c"]).total_len() == 3
