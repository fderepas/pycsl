r"""Test 1772 — WITNESS: a `#@ for ... in range(...)` with an EMPTY body.

The sugar exists to expand a clause per value; with no clauses it expands to nothing while
looking like a specification. Refused rather than expanded to silence.

IT DOES NOT FIRE THE REFUSAL IT WAS WRITTEN FOR, and that is worth stating in the file
rather than only in a plane header. This was written for `Module3_Weaver._desugar_for`'s
`if not c.clauses`; what it actually reports is

    [Module1]: `for i in range(0, 3)`: empty body

— `Module1_Ingestor._fold_blocks`, which requires a 4-space-indented body under every block
header and runs long before the weaver. Lesson (n3): a check that runs first retires the
one behind it, and a witness can be REAL, the refusal REAL, and the two DIFFERENT.

GEN #31 CLOSED THE QUESTION THE OTHER WAY. The Module 3 site is not merely shadowed, it is
UNREACHABLE: `ForExpand` is constructed in exactly one place in the front-end
(`Module2_Parser._parse_for_block`, as its final `return`) and the statement immediately
before it is `if not clauses: self._err("for block requires at least one clause")`. Two
further spellings were run — a body holding only a comment, and a body holding a nested
`#@ for` or an `assigns` — and both are refused by that Module 2 grammar check. So no third
spelling exists to hunt, the site is classified NOT SOURCE-REACHABLE, and it is demonstrated
executably by `bin/check-frontend-ir-backstop-refusals.py`, whose
`forexpand_construction_invariant()` re-derives the invariant from the shipping AST every
run and REFUSES if a second construction site ever appears.

THIS FILE STILL EARNS ITS PLACE: it is the witness for Module 1's block-structure refusal,
which is the check that actually protects the user here.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ requires \length(xs) >= 3
#@ for i in range(0, 3):
#@ ensures \result >= 0
def total(xs: List[int]) -> int:
    return xs[0]
