r"""Test 1879 — gen #31: a dict FIELD whose values are lists now imports `seq.Seq`.

The twin of 1872, ten lines below it in the same emitter block. A field annotated
`Dict[int, List[int]]` resolves its value type to `seq int` — the resolver has handled
`Dict[K, List[T]]` since nested-map.md / #15 — and the emitted record declaration then
names `seq` with no `use seq.Seq` in scope:

    unbound type symbol 'seq'

`needs_seq`'s field clause was character-for-character the same shape as `needs_array`'s,
with the same over-narrow `value_type == "string"` conjunct, from the same relaunch, under
a comment that states the rule correctly ("the record decl is emitted from the FIELD").
One rule, two adjacent disjunctions, implemented for exactly the one witness relaunch #16
had in hand.

Why nobody hit this half before: reaching it needs an ANNOTATED dict field whose values are
lists, and the ordinary spelling (`self.m = m`, typed only on the `__init__` PARAMETER)
degrades the value type to `int` long before the import matters.
"""
# pycsl-expected: PASS
from typing import Dict, List

_ = 0  # anchor


class W:
    def __init__(self, m: Dict[int, List[int]]) -> None:
        self.m: Dict[int, List[int]] = m

    #@ ensures \result >= 0
    #@ assigns \nothing
    def size(self) -> int:
        return 0
