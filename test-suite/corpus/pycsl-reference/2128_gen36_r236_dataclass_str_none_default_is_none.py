r"""Test 2128 — route #236 (expected PASS): CONTROL. An omitted `name: str = None` is
route #50's `pycsl_none_str` (base: the ill-typed int `0`, a refusal), so `p.name is None` is
decided True and `\result == 2` PROVES.
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    x: int
    name: str = None


#@ ensures \result == 2
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.name is None:
        return 2
    return 1
