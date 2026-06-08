"""Test 0642 — constant exec("…") straight-line splice ≡ inline source (07-1839 P5b).

A constant `exec("x = 5\ny = x + 1")` is parsed at verification time (the tool's own `pure_ast.parse`)
and the statements spliced in place — so `y` is in scope for the return and `\result == 6` proves,
exactly as if written inline. The splice emits byte-identical WhyML to the inline form (the soundness
evidence: verification-equivalent, rev4 §8.5).
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == 6
#@ assigns \nothing
def f() -> int:
    exec("x = 5\ny = x + 1")
    return y
