"""Test 0668 — negative: `\length` on a dict is rejected (LOOP-INVARIANT surface).

Same `_validate_predicate_bases` check as 0667, but inside a `#@ loop invariant` —
so the error context is `while loop at line N inside function 'f'`, NOT `function
'f'`. This surface-specific context is exactly what the B4 IR migration must
reproduce, and it requires the IR loop node to carry a source span (statement-level
spans, B4a) + a surface-tracking walk (B4b). The gate driver that forces them.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f(d: dict) -> int:
    i = 0
    #@ loop invariant \length(d) >= 0
    while i < 1:
        i = i + 1
    return 0
