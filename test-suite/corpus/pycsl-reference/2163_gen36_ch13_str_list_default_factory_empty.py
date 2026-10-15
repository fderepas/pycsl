r"""Test 2163 — ch13 seam S-a (expected PASS): a `@dataclass` field `xs: List[str] =
field(default_factory=list)` OMITTED at construction. The field is declared `array string`, but
the record-literal default kept the int element (`(Array.make 0 0)`), so every 0-arg construction
was an L3-tc refusal at base. The default is now the faithful empty `(Array.make 0 "")`: CPython
`R().xs` is falsy (empty). Twins: 2164 (false length), 2165 (int-element control).
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import List


@dataclass
class R:
    xs: List[str] = field(default_factory=list)


#@ ensures \result == k
#@ assigns \nothing
def size_plus(k: int) -> int:
    r = R()
    if r.xs:
        return k + 1
    return k
