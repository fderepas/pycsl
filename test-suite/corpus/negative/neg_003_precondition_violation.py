# pycsl-expected: PASS
#
# (#49) gen #30: THE EXPECTATION IS `PASS`, AND THAT IS NOT A CONTRADICTION.
# This is a DYNAMIC-ORACLE witness, not a static one. `needs_positive`'s own contracts
# (`requires x > 0` / `ensures \result > 0` over `return x * 2`) are TRUE, so the static
# verifier proves them and SHOULD. The violation is the `needs_positive(-1)` call inside
# the `if __name__ == "__main__":` block, which the static verifier does not model — a
# runtime assertion check is what catches it. Marked explicitly because a negative-looking
# filename with no expectation is how a green run gets misread.
#
# Negative test: precondition violation at call site
# Dynamic oracle should catch precondition failure

_ = 0  # anchor for LibCST leading_lines
#@ requires x > 0
#@ ensures \result > 0
def needs_positive(x: int) -> int:
    return x * 2

if __name__ == "__main__":
    print("needs_positive(-1) =", needs_positive(-1))  # precondition violated
