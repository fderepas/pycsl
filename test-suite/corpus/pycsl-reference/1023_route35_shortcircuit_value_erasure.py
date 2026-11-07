"""Test 1023 — ROUTE #35 negative witness: `and`/`or` in a VALUE position returned
a boolean instead of the selected OPERAND.

FALSE OF THE PROGRAM: `0 or 5` is **5** in Python, and `3 and 7` is **7**.

At the parent commit c4233fed both functions proved. The emission was
`x := (if (0 <> 0) || (5 <> 0) then 1 else 0)` — i.e. 1 — because the emitter
lowered `and`/`or` as a Why3 boolean connective and coerced the result back with
`if … then 1 else 0`. The comment above that line said, in as many words, "In
body context, Python's and/or return int". They return an OPERAND.

The lowering was CORRECT IN A CONDITION and WRONG IN A VALUE, and nothing at the
emission site knows which consumer it has, so the value-preserving form is now
emitted wherever it is well-typed — it is equally correct in a condition, because
`_to_bool` then tests the truthiness of the SELECTED operand, which is the
truthiness Python would have tested. Its true twin is 1024.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def f_or() -> int:
    x = 0 or 5
    return x
