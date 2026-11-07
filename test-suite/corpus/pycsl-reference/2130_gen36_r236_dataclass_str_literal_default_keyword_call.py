r"""Test 2130 — route #236 (expected PASS): CONTROL. 2129 through a KEYWORD call that
omits `name` (`P(c, y=4)`): the faithful `"w"` is kept and `\result == 1` PROVES.
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    x: int
    name: str = "w"
    y: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c, y=4)
    if p.name == "w":
        return 1
    return 2
