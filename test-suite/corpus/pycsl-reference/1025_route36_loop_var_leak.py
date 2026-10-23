"""Test 1025 — ROUTE #36 negative witness: the `for` loop variable did not
survive the loop.

FALSE OF THE PROGRAM: Python leaves a loop variable bound to its LAST value, so
`i` is 2 after the loop and Python returns 2.

At the parent commit c4233fed this proved `\result == 0`. The emission opens
`let i = ref (!_idx_i) in` INSIDE the body, so the name is shadowed for the
loop's duration and the OUTER `i` still holds its pre-loop value afterwards.
The binder now assigns the OUTER ref BEFORE opening the inner `let`, which
reproduces Python exactly — including the never-ran case, where the variable
keeps whatever it had.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= 3
    #@ loop variant 3 - i
    for i in range(3):
        pass
    return i
