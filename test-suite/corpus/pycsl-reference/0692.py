"""Test 0692 — negative: undefined variable in a FOR-loop invariant.

A Python `for i in range(n)` desugars to a WhyML `while` only at Module-6 emission,
so at IR-semantic time the node is still a `for`. The contract-scope check
(core_ir_semantic._cs_stmt) now validates a for-loop's invariants exactly as it does a
while-loop's, so an undefined variable in a `#@ loop invariant` on a `for` is caught
with the SAME "Undefined variable ... for loop at line N inside function 'f'" message
the `while` twin produces (cf. 0667). Closes the for/while validation-gap.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f(n: int) -> int:
    s = 0
    #@ loop invariant nosuchvar > 0
    for i in range(n):
        s = s + 1
    return s
