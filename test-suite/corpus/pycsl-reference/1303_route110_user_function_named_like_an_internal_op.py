"""Test 1303 — ROUTE #110 negative witness: `_coerce_to_int` REPLACED A CALL ARGUMENT WITH
THE LITERAL `0` when the lowered argument text happened to start with an internal op
spelling — and seven of those spellings are ordinary Python identifiers.

FALSE OF THE PROGRAM: `any_1(x)` is `x + 1`, which under `x >= 0` is at least 1, never 0.

At the parent commit this PROVED (rc=0) and the emitted list literal was `Array.make 1 (0)`
— the call GONE, the callee's contract discarded. `expressions.py` decided "is this term
array-shaped?" by testing the FIRST CHARACTERS OF GENERATED TEXT against
`("(Array.make", "(Array.sub ", "(array_slice ", "(sorted_1 ", "(list_new_arr ", "(any_1 ",
"(all_1 ")`. `whyml_ident` leaves `any_1` unchanged, so an ordinary call `any_1(x)` lowers
to `(any_1 x)` and matched.

THE ONLY DIFFERENCE BETWEEN A FALSE PROOF AND AN HONEST REFUTATION WAS THE SPELLING OF A
USER-CHOSEN FUNCTION NAME. Renaming the callee `anyq_1` made the identical file fail.

Unlike route #107's `try/else` — five sites in all four trees — `_coerce_to_int` is on the
hot path of list literals, dict keys and values, subscript stores, `setattr`, `for`-loop
iterables and abstract-op arguments. The population was never exotic.

The repair keys the decision on whether the head symbol is a USER-DEFINED function
(`_module_func_names`) rather than on spelling alone, and passes such a term THROUGH: if it
really is collection-typed, Why3 rejects it where an `int` is expected — a loud error
instead of a silent `0`.

The positive twin is 1304.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x0 >= 0
#@ ensures \result == x0 + 1
#@ assigns \nothing
def any_1(x0: int) -> int:
    return x0 + 1

#@ requires x >= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    xs = [any_1(x)]
    return xs[0]
