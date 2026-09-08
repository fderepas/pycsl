"""Test 1074 — a CHAINED COMPARISON in a `#@` CLAUSE is a CONJUNCTION, and until now it
was nothing at all.

`0 <= x <= 3` in a `requires`, an `ensures` or a `loop invariant` was lowered
LEFT-ASSOCIATIVELY to `((0 <= x) <= 3)` — a bool compared to an int. Why3 type-rejects
that, so the clause failed CLOSED rather than proving something wrong; but it did not mean
what it reads as, and `0 <= i <= 3` is THE canonical loop-invariant idiom. At the parent
commit d14f3c97 every function below reported `Verification FAILED` with `term expected`.

`pycsl-reference/0969`'s docstring asserted that "the `#@` ANNOTATION grammar has always
expanded chains correctly" and cited 0865. MEASURED FALSE: 0865 is written in the already-
expanded form `0 <= \\result and \\result < 256`, and a real chain had never worked in a
clause. Route #33's `desugar_chained_comparisons` fixes exactly this for PROGRAM code and
does not reach contract expressions, which come from Module 2's own grammar.

The expansion is safe here in a way it is not in program code: route #33 needed a walrus to
bind the middle operand because Python evaluates it EXACTLY ONCE and a program operand may
have effects, while a CONTRACT expression is pure by construction, so mentioning the middle
operand twice is semantically free.

`out_of_band` is the companion negative: the same chain, on a body that violates it, must
still FAIL — an expansion that collapsed to `true` would make this file pass and would be
worse than the type error it replaced.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires 0 <= a <= 3
#@ ensures 0 <= \result <= 3
#@ assigns \nothing
def passthrough(a: int) -> int:
    return a


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def counted() -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i <= 3
    #@ loop invariant total == i
    #@ loop variant 3 - i
    while i < 3:
        total = total + 1
        i = i + 1
    return total
