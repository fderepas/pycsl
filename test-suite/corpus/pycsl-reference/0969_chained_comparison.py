"""Test 0969 — a CHAINED COMPARISON in Python-expression position is a CONJUNCTION.

`a <= b <= c` is `a <= b and b <= c` in Python, with the middle operand evaluated EXACTLY
ONCE. Module 5's `_py_expr_compare` reads `ops[0]`/`comparators[0]` and nothing else, so
before `frontend/desugar_compare.py` every chain lost its tail: `2 <= a <= 3` lowered to
`2 <= a`.

That is not a harmless over-approximation. A guard TRUE MORE OFTEN than Python's
over-approximates the THEN branch but UNDER-approximates the ELSE: every state with `a >= 2`
and `a > 3` takes Python's else and the model's then, so the else branch was proved over a
strict SUBSET of the reachable states.

It was also an internal disagreement: the `#@` ANNOTATION grammar has always expanded chains
correctly (corpus 0865 emits `ensures { ((0 <= result) && (result < 256)) }`), so the two
halves of the same file meant different things by `a <= b <= c`.

EVERY POSTCONDITION BELOW IS A NEGATIVE TEST of the old behaviour — measured, with the pass
removed, as `Verification FAILED` (7 non-Valid goals):
  * `in_range`   — tail dropped ==> `in_range(7)` returns 1 and `\\result = 1 ==> a <= 3` fails.
  * `ordered3`   — a THREE-comparator chain, so TWO expansion steps must happen; with only
    the first kept, `ordered3(5, 1, 9)` returns 1 and `\\result = 1 ==> a <= b` fails.
  * `size_band`  — the middle operand is `len(arr)`, a PURE TOTAL DETERMINISTIC BUILTIN.
    This is the witness for the `len`/`ord`/`abs`/`chr` allow-list that lets the expansion
    simply mention the operand twice.
  * `call_band`  — the middle operand is a CALL to a user function, which the pass may NOT
    mention twice because Python evaluates it once. It is bound by a WALRUS on its single
    evaluation instead (`a <= (_t := f()) and _t <= b`), so the idiom is supported rather
    than refused. Four reference-corpus files (0836, 0862, 0865, 0867) are written this way.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires True
#@ ensures \result == 1 ==> (2 <= a and a <= 3)
#@ ensures (2 <= a and a <= 3) ==> \result == 1
#@ assigns \nothing
def in_range(a: int) -> int:
    if 2 <= a <= 3:
        return 1
    return 0


#@ requires True
#@ ensures \result == 1 ==> (a <= b and b <= c)
#@ ensures (a <= b and b <= c) ==> \result == 1
#@ assigns \nothing
def ordered3(a: int, b: int, c: int) -> int:
    if a <= b <= c:
        return 1
    return 0


#@ requires \length(arr) >= 0
#@ ensures \result == 1 ==> \length(arr) <= 3
#@ ensures \result == 1 ==> 2 <= \length(arr)
#@ assigns \nothing
def size_band(arr: list) -> int:
    if 2 <= len(arr) <= 3:
        return 1
    return 0


#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def seven() -> int:
    return 7


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def call_band() -> int:
    if 2 <= seven() <= 3:
        return 1
    return 0
