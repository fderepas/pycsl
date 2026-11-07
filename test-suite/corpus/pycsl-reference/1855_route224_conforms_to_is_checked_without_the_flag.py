r"""Test 1855 — ROUTE #224 CLOSED: a declared `#@ conforms_to` is checked by DEFAULT.

Route #224, found by the first run of `bin/check-directive-enforcement.py`: `C.m` ensures
`\result == 1`, which does NOT refine `P.m`'s `\result == 99`, and the DEFAULT run reported

    [+] Verification SUCCESS! All contracts formally proven.

with no warning of any kind. The refinement goal `((pre_P -> pre_C) /\ (post_C -> post_P))`
was emitted only under `--check-behavioral-subtyping`; without it the `(C__m, P__m)` pairs
sat in the IR and nothing read them.

`test-suite/annotations.md` §12.15 said both things three lines apart — that `#@ conforms_to`
synthesizes "per-method contract-refinement VCs", and that the FLAG emits the goal. The
first sentence is the one a reader takes away, and it attributes the VCs to the DIRECTIVE.

The repair is route #224's own priced option 2: the goal follows the DIRECTIVE. A
`#@ conforms_to` pair is now tagged `from_conforms_to` in the `overrides` IR list, and
Module 6 emits the refinement goals for THOSE pairs whether or not the flag is passed. The
IMPLICIT inheritance overrides keep their opt-in behaviour exactly — nobody wrote those
down, so nothing is being checked behind the user's back.

This file carries NO `# pycsl-flags`. It FAILS. Before the repair it verified.

Control: 1856, the same shape with a REFINING contract, which verifies by default — so the
refusal is about the non-refinement and not about `#@ conforms_to`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Protocol


class P(Protocol):
    #@ ensures \result == 99
    def m(self) -> int: ...


#@ conforms_to P
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    def m(self) -> int:
        return 1
