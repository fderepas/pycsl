r"""Test 2129 — route #236 (expected PASS): CONTROL. An omitted `name: str = "w"` takes
its FAITHFUL literal (finding-0700's `field_str_defaults`, now fed from the class body):
`\result.name == "w"` PROVES (base: the ill-typed int `0`, a refusal).
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    x: int
    name: str = "w"


#@ ensures \result.name == "w"
#@ assigns \nothing
def f(c: int) -> P:
    return P(c)
