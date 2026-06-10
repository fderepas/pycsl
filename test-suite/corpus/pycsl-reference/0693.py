"""Test 0693 — negative: dynamic \\proj index in a FOR-loop invariant.

The \\proj-index literal guard is a pre-Module-5 precondition (Module 5's ProjExpr
emission reads `index.value`, assuming a literal). A `for` desugars to a `while` only
at Module-6 emission, so Module 4's visit_For now runs the same _validate_proj_indices
guard visit_While does. Without it, a dynamic \\proj(p, n) in a for-loop invariant
slipped past the guard and CRASHED Module 5 (`'Var' object has no attribute 'value'`);
now it errors cleanly with the SAME "\\proj index must be an integer literal in for loop
at line N inside function 'f'" message its `while` twin produces (cf. 0302).
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
