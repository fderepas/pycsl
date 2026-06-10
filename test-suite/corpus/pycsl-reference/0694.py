"""Test 0694 — negative: \\length on a dict in a FOR-loop invariant.

`\\length` is rejected on a dict (dicts are modelled as total maps with no cardinality).
The predicate-base check (core_ir_semantic._pb_stmt) now walks a for-loop's invariants
exactly as it does a while-loop's, so `\\length(d)` in a `#@ loop invariant` on a `for`
is caught with the SAME "\\length is not supported on the dict-typed 'd' in for loop at
line N inside function 'f'" message its `while` twin produces (cf. 0667-0673). Confirms
the predicate-base surface walk reaches for-loop invariants after the gap fix.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f(d: dict, n: int) -> int:
    s = 0
    #@ loop invariant \length(d) >= 0
    for i in range(n):
        s = s + 1
    return s
