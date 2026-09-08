"""Test 0102 — Python Reference 4.1: Structure of a program"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_structure_of_a_program() -> int:
    """Ref 4.1: a Python program is built from CODE BLOCKS — a function body is one, and
    so is the body of a `while` or an `if`. A block executes as a unit, and a loop body is
    NOT a new scope: names bound outside it are read and written in place. The invariant
    below states exactly the relationship that nesting guarantees between the counter and
    the accumulator, so the obligation is about the block structure rather than about any
    literal. Previously the body was `return 0` and exercised no block at all.

    The invariant is written `0 <= i and i <= 3` rather than the idiomatic chain
    `0 <= i <= 3`, and that is a MEASURED limitation, not a preference: a chained
    comparison inside a `#@` clause is lowered LEFT-ASSOCIATIVELY, so `0 <= i <= 3`
    becomes `((0 <= !i) <= 3)` — a bool compared to an int. Why3 type-rejects it, so it
    fails closed rather than proving something wrong, but the clause does not mean what it
    reads as. Module 5's `desugar_chained_comparisons` fixes exactly this for PROGRAM code
    (route #33) and does not reach contract expressions."""
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= 3
    #@ loop invariant total == i
    #@ loop variant 3 - i
    while i < 3:
        total = total + 1
        i = i + 1
    if total == 4:
        return 0
    return 1

if __name__ == "__main__":
    assert test_structure_of_a_program() == 0
