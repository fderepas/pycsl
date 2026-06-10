"""Test 0693 — negative: dynamic \\proj index in a FOR-loop invariant.

The \\proj-index literal guard lives at Module 5's ProjExpr emission site (B-final
STEP 1): emission reads `index.value`, which only exists on a literal. A dynamic
\\proj(p, n) in a for-loop invariant would crash that emission (`'Var' object has no
attribute 'value'`); the guard raises first with "\\proj index must be an integer
literal in function 'f'. Dynamic projection is not supported." (the guard's surface
context narrowed to the enclosing function when it moved out of Module 4's per-surface
visit_For/visit_While; cf. 0302, its function-surface twin).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0 and n < 2
#@ assigns \nothing
def f(n: int) -> int:
    #@ ghost p : tuple2 = \mktuple(10, 20)
    s = 0
    #@ loop invariant \proj(p, n) >= 0
    for i in range(n):
        s = s + 1
    return s
