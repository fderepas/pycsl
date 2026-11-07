"""Test 0988 — a collection PARAMETER that a function's own contract NAMES may not be
mutated in place, even inside a `@mutable_state` class. It used to prove a postcondition
that is FALSE of the program.

`_handle_expr_stmt` lowers a set/dict-typed PARAM mutated via `.add`/`.discard`/`.remove`
inside a `@mutable_state` class to a NO-OP, justified in the source as:

    the mutation is on a value param, so it does NOT escape for an `assigns \nothing` /
    type-safety contract: a sound no-op. (A Python set param IS mutated, but no contract
    here reads it — the recursion's `declared_refs` is a trusted sibling arg.)

"no contract here reads it" is a claim about the corpus as it stands, not a property of the
lowering. Measured, before this refusal:

    @mutable_state
    class C:
        #@ requires 1 not in s
        #@ ensures 1 not in s              <-- FALSE OF THE PROGRAM
        #@ assigns \nothing
        def m(self, s: Set[int]) -> None:
            s.add(1)

    [+] Verification SUCCESS! All contracts formally proven.

THE CONTROL IS WHAT MAKES IT SHARP: the IDENTICAL class WITHOUT `@mutable_state` is
REJECTED outright by the WL-05 caller-visible-mutation boundary. The decorator was turning
a hard refusal into a silent no-op.

The exemption now holds only while its own justification does: the mutated parameter must
not be NAMED in any contract clause. That was measured against the blunt alternative —
removing the exemption entirely breaks THREE mirror files (`expressions`, `statements`,
`stmt_control_flow`), whose reflecting handlers really do mutate sibling `declared_refs`
style arguments and never name one in a contract, so this check leaves all of them alone.

Two narrowings were needed and both were measured, not guessed: restricting the mutator set
to `.add`/`.discard`/`.remove` on a SET/DICT-typed formal (the first spelling also caught
`ir_stmts.append(...)`, a contract-named LIST param with a FAITHFUL `Seq.snoc` lowering,
and broke `Module5_IREmitter` and `pycsl.py`); and comparing `whyml_ident(name.lower())`
against `_mutable_state_classes`, which holds the lowered spelling, not the source name.

CENSUS: corpus emission BYTE-IDENTICAL across `pycsl-reference` (820) AND `python-reference`
(2144), mirror emission byte-identical, mirror L3-tc 53/53.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import Set


@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.n
    def __init__(self) -> None:
        self.n: int = 0

    #@ requires 1 not in s
    #@ ensures 1 not in s
    #@ assigns \nothing
    def m(self, s: Set[int]) -> None:
        s.add(1)
