# ROUTE #36 RESIDUE — OPEN AT THE END OF RELAUNCH #45. This file is a
# REPRODUCTION, not a corpus test: it PROVES today and its contract is FALSE of
# the program (Python returns 7), so putting it in the corpus would be an XPASS —
# a suite FAILURE — rather than a witness. Move it to
# `test-suite/corpus/pycsl-reference/1027_...` in the increment that closes it.
#
# WHAT IS CLOSED AND WHAT IS NOT. The INDEX-valued case
# (`for i in range(n)` then a read of `i`) is closed: the binder assigns the OUTER
# ref before opening the inner `let`, which reproduces Python exactly. Witnesses
# 1025/1026. This file is the SEQUENCE case, and it is not closed.
#
# THE OBSTACLE, MEASURED THREE WAYS AT THE BINDER:
#   * an unconditional element write-back  -> mirror L3-tc 51/53
#     (`expressions.py`, `functions.py`)
#   * an `any int` havoc after the loop    -> mirror L3-tc 52/53
#     (`stmt_control_flow.py`, whose loop target ref is `emit_ir`-typed)
#   * restricting to targets not assigned elsewhere in the function -> still
#     51/53, and it moves four mirror emissions. The "assigned elsewhere" test is
#     NOT the right proxy for the type mismatch.
# The outer ref takes its type from the FIRST assignment to that name, which need
# not be the loop's element type, and the binder does not have that type. Get the
# declared WhyML type of the outer ref to the binder and this is a one-line
# widening of the existing `_r36_wb` condition in
# `module6_whyml/stmt_control_flow.py`.
#
# A REFUSAL IS NOT AN OPTION HERE and that was measured too: refusing every
# `for` target read outside its loop breaks 14 of the 53 mirror files, because
# reading a loop variable after its loop is an idiom the emitter itself uses.

_ = 0  # anchor
#@ requires \length(a) == 2
#@ requires a[0] == 1
#@ requires a[1] == 7
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    """FALSE OF THE PROGRAM: after the loop x is the LAST element, 7, so Python
    returns 7."""
    x = 0
    for x in a:
        pass
    return x
